/**
 * ============================================================================
 * PC PERFORMANCE BENCHMARK & BOTTLENECK ANALYSIS SUITE
 * PHASE 3 — CPU MULTI-THREAD BENCHMARK (OPENMP)
 * ============================================================================
 * 
 * Target Architecture: Intel Core i5-11400H (6 Physical Cores / 12 Threads)
 * Multi-threading API: OpenMP 2.0 / MSVC OpenMP Runtime (/openmp)
 * Language: C++20 (MSVC)
 * Dependencies: Win32 APIs, Powrprof, WMI (COM), OpenMP (<omp.h>)
 * 
 * Output: Terminal Report + results/cpu_multi.json
 * ============================================================================
 */

#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <chrono>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <cstdint>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <powrprof.h>
#include <intrin.h>
#include <wbemidl.h>
#include <comdef.h>
#include <omp.h>

#pragma comment(lib, "Powrprof.lib")
#pragma comment(lib, "wbemuuid.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")
#pragma comment(lib, "Advapi32.lib")

// ============================================================================
// DATA STRUCTURES
// ============================================================================

struct MultiThreadResult {
    int threadCount = 0;
    double executionTimeSec = 0.0;
    double throughputGflops = 0.0;
    double actualScaling = 0.0;
    double idealScaling = 0.0;
    double efficiencyPercent = 0.0;

    double cpuUtilizationPercent = 0.0;
    double cpuFrequencyMhz = 0.0;
    double cpuTemperatureCelsius = 0.0;
};

// ============================================================================
// CPU TELEMETRY HELPERS (UTILIZATION, FREQUENCY, TEMPERATURE)
// ============================================================================

static uint64_t FileTimeToUInt64(const FILETIME& ft) {
    return (static_cast<uint64_t>(ft.dwHighDateTime) << 32) | ft.dwLowDateTime;
}

class SystemTelemetry {
private:
    uint64_t prevIdle = 0;
    uint64_t prevKernel = 0;
    uint64_t prevUser = 0;
    IWbemServices* pSvc = nullptr;
    IWbemLocator* pLoc = nullptr;
    bool wmiReady = false;

public:
    SystemTelemetry() {
        FILETIME idle, kernel, user;
        if (GetSystemTimes(&idle, &kernel, &user)) {
            prevIdle = FileTimeToUInt64(idle);
            prevKernel = FileTimeToUInt64(kernel);
            prevUser = FileTimeToUInt64(user);
        }

        HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
        if (SUCCEEDED(hr) || hr == RPC_E_CHANGED_MODE) {
            hr = CoCreateInstance(CLSID_WbemLocator, 0, CLSCTX_INPROC_SERVER,
                                  IID_IWbemLocator, (LPVOID*)&pLoc);
            if (SUCCEEDED(hr) && pLoc) {
                hr = pLoc->ConnectServer(_bstr_t(L"ROOT\\CIMV2"), nullptr, nullptr, 0,
                                         0, 0, 0, &pSvc);
                if (SUCCEEDED(hr) && pSvc) {
                    CoSetProxyBlanket(pSvc, RPC_C_AUTHN_WINNT, RPC_C_AUTHZ_NONE, nullptr,
                                      RPC_C_AUTHN_LEVEL_CALL, RPC_C_IMP_LEVEL_IMPERSONATE,
                                      nullptr, EOAC_NONE);
                    wmiReady = true;
                }
            }
        }
    }

    ~SystemTelemetry() {
        if (pSvc) pSvc->Release();
        if (pLoc) pLoc->Release();
        CoUninitialize();
    }

    void ResetCpuUtilization() {
        FILETIME idle, kernel, user;
        if (GetSystemTimes(&idle, &kernel, &user)) {
            prevIdle = FileTimeToUInt64(idle);
            prevKernel = FileTimeToUInt64(kernel);
            prevUser = FileTimeToUInt64(user);
        }
    }

    double GetCpuUtilization() {
        FILETIME idle, kernel, user;
        if (!GetSystemTimes(&idle, &kernel, &user)) return 0.0;

        uint64_t nowIdle = FileTimeToUInt64(idle);
        uint64_t nowKernel = FileTimeToUInt64(kernel);
        uint64_t nowUser = FileTimeToUInt64(user);

        uint64_t dIdle = nowIdle - prevIdle;
        uint64_t dKernel = nowKernel - prevKernel;
        uint64_t dUser = nowUser - prevUser;

        uint64_t totalSys = dKernel + dUser;
        if (totalSys == 0) return 0.0;

        double util = 100.0 * (1.0 - static_cast<double>(dIdle) / static_cast<double>(totalSys));
        return (util < 0.0) ? 0.0 : (util > 100.0 ? 100.0 : util);
    }

    double MeasureActiveFrequencyMhz() {
        LARGE_INTEGER qpcFreq, qpcStart, qpcEnd;
        QueryPerformanceFrequency(&qpcFreq);
        QueryPerformanceCounter(&qpcStart);
        uint64_t tscStart = __rdtsc();

        // 30ms calibration window
        double targetSec = 0.030;
        double elapsedSec = 0.0;
        do {
            QueryPerformanceCounter(&qpcEnd);
            elapsedSec = static_cast<double>(qpcEnd.QuadPart - qpcStart.QuadPart) / qpcFreq.QuadPart;
        } while (elapsedSec < targetSec);

        uint64_t tscEnd = __rdtsc();
        double measuredHz = static_cast<double>(tscEnd - tscStart) / elapsedSec;
        return measuredHz / 1e6;
    }

    double GetCpuTemperature() {
        if (!wmiReady || !pSvc) return 0.0;
        IEnumWbemClassObject* pEnum = nullptr;
        HRESULT hr = pSvc->ExecQuery(
            bstr_t("WQL"),
            bstr_t("SELECT Temperature FROM Win32_PerfFormattedData_Counters_ThermalZoneInformation"),
            WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY, nullptr, &pEnum);

        double tempC = 0.0;
        if (SUCCEEDED(hr) && pEnum) {
            IWbemClassObject* pObj = nullptr;
            ULONG uReturn = 0;
            if (pEnum->Next(WBEM_INFINITE, 1, &pObj, &uReturn) == S_OK && uReturn > 0) {
                VARIANT vtProp;
                if (SUCCEEDED(pObj->Get(L"Temperature", 0, &vtProp, 0, 0))) {
                    if (vtProp.vt == VT_UI4 || vtProp.vt == VT_I4) {
                        uint32_t rawKelvinTenths = vtProp.uintVal;
                        if (rawKelvinTenths > 2730) {
                            tempC = (rawKelvinTenths - 2732) / 10.0;
                        } else if (rawKelvinTenths > 200 && rawKelvinTenths < 400) {
                            tempC = rawKelvinTenths - 273.15;
                        }
                    }
                    VariantClear(&vtProp);
                }
                pObj->Release();
            }
            pEnum->Release();
        }
        return tempC;
    }
};

// ============================================================================
// COMPUTE WORKLOAD KERNEL (PARALLEL NUMERICAL INTEGRATION / FMA MATRIX ENGINE)
// ============================================================================

// Each element computes an arithmetic polynomial series with 16 FLOPs per step
static double ComputeBlock(int64_t startIdx, int64_t count) {
    double total = 0.0;
    for (int64_t i = 0; i < count; ++i) {
        double x = static_cast<double>(startIdx + i) * 0.0000001;
        double a = x * 1.0001 + 0.5001;
        double b = a * 0.9999 - 0.2001;
        double c = b * 1.0002 + 0.1002;
        double d = c * 0.9998 - 0.0501;

        total += (a * b + c * d) * 0.00001;
    }
    return total;
}

static double RunParallelWorkload(int threadCount, int64_t totalElements, double& outSum) {
    omp_set_num_threads(threadCount);

    double globalSum = 0.0;
    auto t0 = std::chrono::high_resolution_clock::now();

    #pragma omp parallel for reduction(+:globalSum) schedule(static)
    for (int64_t i = 0; i < totalElements; ++i) {
        double x = static_cast<double>(i) * 0.00000001;
        // 16 floating-point operations per step
        double a = x * 1.00001 + 0.50001;
        double b = a * 0.99999 - 0.20001;
        double c = b * 1.00002 + 0.10002;
        double d = c * 0.99998 - 0.05001;
        globalSum += (a * b + c * d);
    }

    auto t1 = std::chrono::high_resolution_clock::now();
    outSum = globalSum;
    return std::chrono::duration<double>(t1 - t0).count();
}

// ============================================================================
// TERMINAL DASHBOARD & ANALYSIS
// ============================================================================

static void PrintMultiThreadReport(const std::vector<MultiThreadResult>& results) {
    std::cout << "\n==================================================================================================\n";
    std::cout << "                      PHASE 3: CPU MULTI-THREAD SCALING BENCHMARK (OPENMP)                        \n";
    std::cout << "==================================================================================================\n";
    std::cout << " Hardware: Intel Core i5-11400H (6 Physical Cores, 12 Logical Processors)\n";
    std::cout << " Architecture Note: Cores 1-6 are Physical. Threads 7-12 share execution pipelines via SMT.\n";
    std::cout << "--------------------------------------------------------------------------------------------------\n";
    std::cout << " Threads | Time (s) | Throughput  | Actual Scale | Ideal Scale | Efficiency | CPU Util | Freq (MHz) | Temp \n";
    std::cout << "---------+----------+-------------+--------------+-------------+------------+----------+------------+------\n";

    for (const auto& r : results) {
        std::cout << " " << std::right << std::setw(7) << r.threadCount << " | "
                  << std::setw(8) << std::fixed << std::setprecision(4) << r.executionTimeSec << " | "
                  << std::setw(7) << std::fixed << std::setprecision(2) << r.throughputGflops << " GFLOPs | "
                  << std::setw(10) << std::fixed << std::setprecision(2) << r.actualScaling << "x | "
                  << std::setw(9) << std::fixed << std::setprecision(2) << r.idealScaling << "x | "
                  << std::setw(8) << std::fixed << std::setprecision(1) << r.efficiencyPercent << " % | "
                  << std::setw(6) << std::fixed << std::setprecision(1) << r.cpuUtilizationPercent << "% | "
                  << std::setw(8) << std::fixed << std::setprecision(0) << r.cpuFrequencyMhz << " | "
                  << std::setw(4) << (int)r.cpuTemperatureCelsius << " C\n";
    }

    std::cout << "--------------------------------------------------------------------------------------------------\n";

    std::cout << "\n[ARCHITECTURAL ANALYSIS & SCALING LAWS]\n";
    std::cout << "  1. Physical Cores (1 to 6 Threads):\n";
    std::cout << "     Each thread gets a dedicated Willow Cove core with full private L1/L2 caches and execution units.\n";
    std::cout << "     Scaling is typically 85%-98% efficient, limited only by all-core turbo frequency drop (PL1/PL2).\n";
    std::cout << "\n  2. Simultaneous Multithreading / Hyper-Threading (7 to 12 Threads):\n";
    std::cout << "     Logical threads 7-12 DO NOT provide additional execution units. They only utilize idle execution\n";
    std::cout << "     bubbles while primary threads wait on cache misses. Expected SMT gain is +20% to +35%, NOT +100%.\n";
    std::cout << "     Therefore, 12 logical threads will never achieve 12x throughput under pure compute loads.\n";
    std::cout << "==================================================================================================\n";
}

static void SaveJson(const std::vector<MultiThreadResult>& results, const std::string& filepath) {
    std::ofstream f(filepath);
    if (!f.is_open()) return;

    f << "{\n";
    f << "  \"timestamp\": \"" << __DATE__ << " " << __TIME__ << "\",\n";
    f << "  \"cpu\": \"Intel Core i5-11400H\",\n";
    f << "  \"physical_cores\": 6,\n";
    f << "  \"logical_processors\": 12,\n";
    f << "  \"results\": [\n";

    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        f << "    {\n";
        f << "      \"threads\": " << r.threadCount << ",\n";
        f << "      \"time_sec\": " << r.executionTimeSec << ",\n";
        f << "      \"throughput_gflops\": " << r.throughputGflops << ",\n";
        f << "      \"actual_scaling\": " << r.actualScaling << ",\n";
        f << "      \"ideal_scaling\": " << r.idealScaling << ",\n";
        f << "      \"efficiency_percent\": " << r.efficiencyPercent << ",\n";
        f << "      \"cpu_utilization_percent\": " << r.cpuUtilizationPercent << ",\n";
        f << "      \"cpu_frequency_mhz\": " << r.cpuFrequencyMhz << ",\n";
        f << "      \"cpu_temperature_c\": " << r.cpuTemperatureCelsius << "\n";
        f << "    }";
        if (i + 1 < results.size()) f << ",";
        f << "\n";
    }
    f << "  ]\n";
    f << "}\n";
    f.close();
    std::cout << "[INFO] Multi-thread telemetry exported to: " << filepath << "\n";
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

int main() {
    SystemTelemetry telemetry;

    // The thread configurations requested: 1, 2, 3, 4, 5, 6, 8, 10, 12
    const std::vector<int> threadConfigs = {1, 2, 3, 4, 5, 6, 8, 10, 12};
    const int64_t totalElements = 120'000'000; // 120M elements * 16 FLOPs = 1.92 GFLOPs per run

    std::cout << "[INFO] Initializing Phase 3 CPU Multi-Thread Scaling Benchmark...\n";
    std::cout << "       Total Workload: 1.92 GFLOPs per configuration.\n";
    std::cout << "       Warming up CPU pipelines...\n\n";

    // Warm-up run
    double dummySum = 0.0;
    RunParallelWorkload(2, 10'000'000, dummySum);

    std::vector<MultiThreadResult> results;
    double singleThreadTime = 0.0;

    for (size_t i = 0; i < threadConfigs.size(); ++i) {
        int threads = threadConfigs[i];
        std::cout << "  [" << (i + 1) << "/" << threadConfigs.size() 
                  << "] Benchmarking " << std::setw(2) << threads << " thread(s)..." << std::flush;

        telemetry.ResetCpuUtilization();

        double sum = 0.0;
        double elapsed = RunParallelWorkload(threads, totalElements, sum);

        double util = telemetry.GetCpuUtilization();
        double freq = telemetry.MeasureActiveFrequencyMhz();
        double temp = telemetry.GetCpuTemperature();

        if (threads == 1) {
            singleThreadTime = elapsed;
        }

        MultiThreadResult r;
        r.threadCount = threads;
        r.executionTimeSec = elapsed;
        r.throughputGflops = (1.92) / elapsed; // 1.92 GFLOPs / seconds
        r.actualScaling = (singleThreadTime > 0.0) ? (singleThreadTime / elapsed) : 1.0;
        r.idealScaling = static_cast<double>(threads);
        r.efficiencyPercent = (r.idealScaling > 0.0) ? (r.actualScaling / r.idealScaling) * 100.0 : 0.0;
        r.cpuUtilizationPercent = util;
        r.cpuFrequencyMhz = freq;
        r.cpuTemperatureCelsius = temp;

        results.push_back(r);

        std::cout << " Done in " << std::fixed << std::setprecision(3) << elapsed << " s (" 
                  << std::setprecision(1) << r.throughputGflops << " GFLOPs, "
                  << std::setprecision(2) << r.actualScaling << "x scaling)\n";
    }

    PrintMultiThreadReport(results);
    SaveJson(results, "results/cpu_multi.json");

    return 0;
}
