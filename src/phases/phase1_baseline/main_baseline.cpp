/**
 * ============================================================================
 * PC PERFORMANCE BENCHMARK & BOTTLENECK ANALYSIS SUITE
 * PHASE 1 — SYSTEM BASELINE & SENSOR CALIBRATION
 * ============================================================================
 * 
 * Target Platform: Windows 10/11 x64
 * Primary Hardware: Intel Core i5-11400H + NVIDIA GeForce GTX 1650 Laptop GPU
 * Language: C++20 (MSVC)
 * Dependencies: Win32 APIs, WMI (COM), Powrprof, dynamic NVML.
 * 
 * Output: Terminal Report + results/cpu_gpu_baseline.json
 * ============================================================================
 */

#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cmath>
#include <numeric>
#include <chrono>
#include <thread>
#include <cstdint>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <powrprof.h>
#include <intrin.h>
#include <wbemidl.h>
#include <comdef.h>

#pragma comment(lib, "Powrprof.lib")
#pragma comment(lib, "wbemuuid.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")
#pragma comment(lib, "Advapi32.lib")

// ============================================================================
// DATA STRUCTURES FOR BASELINE TELEMETRY
// ============================================================================

struct ProcessorPowerInfo {
    ULONG number;
    ULONG maxMhz;
    ULONG currentMhz;
    ULONG mhzLimit;
    ULONG maxIdleState;
    ULONG currentIdleState;
};

struct BaselineSample {
    int sampleIndex = 0;
    double timestampSec = 0.0;

    // CPU Metrics
    double cpuUtilizationPercent = 0.0;
    double cpuCurrentAvgMhz = 0.0;
    double cpuEffectiveMhz = 0.0;
    double cpuTempCelsius = 0.0;
    std::vector<uint32_t> coreMhz;

    // GPU Metrics (NVML)
    bool gpuDetected = false;
    uint32_t gpuCoreClockMhz = 0;
    uint32_t gpuMemClockMhz = 0;
    uint32_t gpuTempCelsius = 0;
    float gpuPowerWatts = 0.0f;
    uint32_t gpuCoreUtilPercent = 0;
    uint32_t gpuMemUtilPercent = 0;

    // RAM Metrics
    uint64_t ramTotalMB = 0;
    uint64_t ramUsedMB = 0;
    uint64_t ramAvailableMB = 0;
    uint32_t ramLoadPercent = 0;
};

struct MetricStats {
    double minVal = 0.0;
    double maxVal = 0.0;
    double avgVal = 0.0;
    double stdDev = 0.0;

    void Compute(const std::vector<double>& vals) {
        if (vals.empty()) return;
        minVal = vals[0];
        maxVal = vals[0];
        double sum = 0.0;
        for (double v : vals) {
            if (v < minVal) minVal = v;
            if (v > maxVal) maxVal = v;
            sum += v;
        }
        avgVal = sum / vals.size();
        double varSum = 0.0;
        for (double v : vals) {
            varSum += (v - avgVal) * (v - avgVal);
        }
        stdDev = std::sqrt(varSum / vals.size());
    }
};

struct AggregatedBaseline {
    MetricStats cpuUtil;
    MetricStats cpuClock;
    MetricStats cpuEffectiveClock;
    MetricStats cpuTemp;

    MetricStats gpuClock;
    MetricStats gpuMemClock;
    MetricStats gpuTemp;
    MetricStats gpuPower;
    MetricStats gpuUtil;

    MetricStats ramUsedMB;
    MetricStats ramLoad;
};

// ============================================================================
// DYNAMIC NVML BINDINGS
// ============================================================================

typedef int nvmlReturn_t;
typedef void* nvmlDevice_t;
typedef struct {
    unsigned int gpu;
    unsigned int memory;
} nvmlUtilization_t;

typedef struct {
    unsigned long long total;
    unsigned long long free;
    unsigned long long used;
} nvmlMemory_t;

typedef nvmlReturn_t (*pfn_nvmlInit_v2)();
typedef nvmlReturn_t (*pfn_nvmlShutdown)();
typedef nvmlReturn_t (*pfn_nvmlDeviceGetHandleByIndex_v2)(unsigned int, nvmlDevice_t*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetClockInfo)(nvmlDevice_t, int, unsigned int*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetTemperature)(nvmlDevice_t, int, unsigned int*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetPowerUsage)(nvmlDevice_t, unsigned int*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetUtilizationRates)(nvmlDevice_t, nvmlUtilization_t*);

class NvmlMonitor {
private:
    HMODULE hNvml = nullptr;
    nvmlDevice_t dev = nullptr;
    pfn_nvmlInit_v2 fn_init = nullptr;
    pfn_nvmlShutdown fn_shutdown = nullptr;
    pfn_nvmlDeviceGetHandleByIndex_v2 fn_getHandle = nullptr;
    pfn_nvmlDeviceGetClockInfo fn_getClock = nullptr;
    pfn_nvmlDeviceGetTemperature fn_getTemp = nullptr;
    pfn_nvmlDeviceGetPowerUsage fn_getPower = nullptr;
    pfn_nvmlDeviceGetUtilizationRates fn_getUtil = nullptr;
    bool active = false;

public:
    NvmlMonitor() {
        hNvml = LoadLibraryA("nvml.dll");
        if (!hNvml) return;

        fn_init = (pfn_nvmlInit_v2)GetProcAddress(hNvml, "nvmlInit_v2");
        fn_shutdown = (pfn_nvmlShutdown)GetProcAddress(hNvml, "nvmlShutdown");
        fn_getHandle = (pfn_nvmlDeviceGetHandleByIndex_v2)GetProcAddress(hNvml, "nvmlDeviceGetHandleByIndex_v2");
        fn_getClock = (pfn_nvmlDeviceGetClockInfo)GetProcAddress(hNvml, "nvmlDeviceGetClockInfo");
        fn_getTemp = (pfn_nvmlDeviceGetTemperature)GetProcAddress(hNvml, "nvmlDeviceGetTemperature");
        fn_getPower = (pfn_nvmlDeviceGetPowerUsage)GetProcAddress(hNvml, "nvmlDeviceGetPowerUsage");
        fn_getUtil = (pfn_nvmlDeviceGetUtilizationRates)GetProcAddress(hNvml, "nvmlDeviceGetUtilizationRates");

        if (fn_init && fn_init() == 0) {
            if (fn_getHandle && fn_getHandle(0, &dev) == 0) {
                active = true;
            }
        }
    }

    ~NvmlMonitor() {
        if (active && fn_shutdown) fn_shutdown();
        if (hNvml) FreeLibrary(hNvml);
    }

    bool IsActive() const { return active; }

    void Sample(BaselineSample& s) {
        if (!active || !dev) return;
        s.gpuDetected = true;

        unsigned int coreClock = 0;
        if (fn_getClock && fn_getClock(dev, 0 /* Graphics */, &coreClock) == 0) {
            s.gpuCoreClockMhz = coreClock;
        }

        unsigned int memClock = 0;
        if (fn_getClock && fn_getClock(dev, 2 /* Memory */, &memClock) == 0) {
            s.gpuMemClockMhz = memClock;
        }

        unsigned int temp = 0;
        if (fn_getTemp && fn_getTemp(dev, 0 /* GPU temp */, &temp) == 0) {
            s.gpuTempCelsius = temp;
        }

        unsigned int powerMW = 0;
        if (fn_getPower && fn_getPower(dev, &powerMW) == 0) {
            s.gpuPowerWatts = powerMW / 1000.0f;
        }

        nvmlUtilization_t util;
        if (fn_getUtil && fn_getUtil(dev, &util) == 0) {
            s.gpuCoreUtilPercent = util.gpu;
            s.gpuMemUtilPercent = util.memory;
        }
    }
};

// ============================================================================
// CPU MEASUREMENT SENSORS
// ============================================================================

static uint64_t FileTimeToUInt64(const FILETIME& ft) {
    return (static_cast<uint64_t>(ft.dwHighDateTime) << 32) | ft.dwLowDateTime;
}

class CpuMonitor {
private:
    uint64_t prevIdleTime = 0;
    uint64_t prevKernelTime = 0;
    uint64_t prevUserTime = 0;
    int numLogicalProcessors = 0;

    IWbemLocator* pLoc = nullptr;
    IWbemServices* pSvc = nullptr;
    bool wmiReady = false;

    void InitWmi() {
        HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
        if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) return;

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

public:
    CpuMonitor(int logicalProcessors) : numLogicalProcessors(logicalProcessors) {
        FILETIME idle, kernel, user;
        if (GetSystemTimes(&idle, &kernel, &user)) {
            prevIdleTime = FileTimeToUInt64(idle);
            prevKernelTime = FileTimeToUInt64(kernel);
            prevUserTime = FileTimeToUInt64(user);
        }
        InitWmi();
    }

    ~CpuMonitor() {
        if (pSvc) pSvc->Release();
        if (pLoc) pLoc->Release();
        CoUninitialize();
    }

    double SampleUtilization() {
        FILETIME idle, kernel, user;
        if (!GetSystemTimes(&idle, &kernel, &user)) return 0.0;

        uint64_t nowIdle = FileTimeToUInt64(idle);
        uint64_t nowKernel = FileTimeToUInt64(kernel);
        uint64_t nowUser = FileTimeToUInt64(user);

        uint64_t dIdle = nowIdle - prevIdleTime;
        uint64_t dKernel = nowKernel - prevKernelTime;
        uint64_t dUser = nowUser - prevUserTime;

        prevIdleTime = nowIdle;
        prevKernelTime = nowKernel;
        prevUserTime = nowUser;

        uint64_t totalSys = dKernel + dUser;
        if (totalSys == 0) return 0.0;

        double util = 100.0 * (1.0 - static_cast<double>(dIdle) / static_cast<double>(totalSys));
        return (util < 0.0) ? 0.0 : (util > 100.0 ? 100.0 : util);
    }

    void SampleClocks(BaselineSample& s) {
        if (numLogicalProcessors <= 0) return;

        std::vector<ProcessorPowerInfo> info(numLogicalProcessors);
        int bufSize = static_cast<int>(numLogicalProcessors * sizeof(ProcessorPowerInfo));

        // CallNtPowerInformation with ProcessorInformation
        LONG status = CallNtPowerInformation(ProcessorInformation, nullptr, 0, info.data(), bufSize);
        if (status == 0) {
            double sumMhz = 0.0;
            s.coreMhz.clear();
            for (int i = 0; i < numLogicalProcessors; ++i) {
                s.coreMhz.push_back(info[i].currentMhz);
                sumMhz += info[i].currentMhz;
            }
            s.cpuCurrentAvgMhz = sumMhz / numLogicalProcessors;
        }
    }

    double SampleEffectiveClock(int sampleDurationMs = 50) {
        LARGE_INTEGER qpcFreq, qpcStart, qpcEnd;
        QueryPerformanceFrequency(&qpcFreq);

        QueryPerformanceCounter(&qpcStart);
        uint64_t tscStart = __rdtsc();

        // Busy spin for sampleDurationMs to calibrate unhalted core cycles
        double targetSec = sampleDurationMs / 1000.0;
        double elapsedSec = 0.0;
        do {
            QueryPerformanceCounter(&qpcEnd);
            elapsedSec = static_cast<double>(qpcEnd.QuadPart - qpcStart.QuadPart) / qpcFreq.QuadPart;
        } while (elapsedSec < targetSec);

        uint64_t tscEnd = __rdtsc();
        uint64_t tscDelta = tscEnd - tscStart;

        double measuredHz = static_cast<double>(tscDelta) / elapsedSec;
        return measuredHz / 1e6; // in MHz
    }

    double SampleTemperature() {
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
                        // Formula: Celsius = (TenthsKelvin - 2732) / 10.0 or (K - 273.15)
                        if (rawKelvinTenths > 2730) {
                            tempC = (rawKelvinTenths - 2732) / 10.0;
                        } else if (rawKelvinTenths > 200 && rawKelvinTenths < 400) {
                            // Already in Kelvin whole units
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
// RAM SAMPLER
// ============================================================================

static void SampleRam(BaselineSample& s) {
    MEMORYSTATUSEX memStatus;
    memStatus.dwLength = sizeof(memStatus);
    if (GlobalMemoryStatusEx(&memStatus)) {
        s.ramTotalMB = memStatus.ullTotalPhys / (1024 * 1024);
        s.ramAvailableMB = memStatus.ullAvailPhys / (1024 * 1024);
        s.ramUsedMB = s.ramTotalMB - s.ramAvailableMB;
        s.ramLoadPercent = memStatus.dwMemoryLoad;
    }
}

// ============================================================================
// BASELINE RUNNER & STATS AGGREGATOR
// ============================================================================

static AggregatedBaseline ComputeAggregates(const std::vector<BaselineSample>& samples) {
    AggregatedBaseline agg;
    std::vector<double> cpuUtil, cpuClock, cpuEffClock, cpuTemp;
    std::vector<double> gpuClock, gpuMemClock, gpuTemp, gpuPower, gpuUtil;
    std::vector<double> ramUsed, ramLoad;

    for (const auto& s : samples) {
        cpuUtil.push_back(s.cpuUtilizationPercent);
        cpuClock.push_back(s.cpuCurrentAvgMhz);
        cpuEffClock.push_back(s.cpuEffectiveMhz);
        if (s.cpuTempCelsius > 0.0) cpuTemp.push_back(s.cpuTempCelsius);

        if (s.gpuDetected) {
            gpuClock.push_back(s.gpuCoreClockMhz);
            gpuMemClock.push_back(s.gpuMemClockMhz);
            gpuTemp.push_back(s.gpuTempCelsius);
            gpuPower.push_back(s.gpuPowerWatts);
            gpuUtil.push_back(s.gpuCoreUtilPercent);
        }

        ramUsed.push_back(static_cast<double>(s.ramUsedMB));
        ramLoad.push_back(static_cast<double>(s.ramLoadPercent));
    }

    agg.cpuUtil.Compute(cpuUtil);
    agg.cpuClock.Compute(cpuClock);
    agg.cpuEffectiveClock.Compute(cpuEffClock);
    agg.cpuTemp.Compute(cpuTemp);

    agg.gpuClock.Compute(gpuClock);
    agg.gpuMemClock.Compute(gpuMemClock);
    agg.gpuTemp.Compute(gpuTemp);
    agg.gpuPower.Compute(gpuPower);
    agg.gpuUtil.Compute(gpuUtil);

    agg.ramUsedMB.Compute(ramUsed);
    agg.ramLoad.Compute(ramLoad);

    return agg;
}

static void PrintBaselineDashboard(const std::vector<BaselineSample>& samples, const AggregatedBaseline& agg) {
    std::cout << "\n================================================================================\n";
    std::cout << "                 PHASE 1: SYSTEM BASELINE CALIBRATION REPORT                    \n";
    std::cout << "================================================================================\n";

    std::cout << "\n[1. LIVE SAMPLE TIMELINE (CALM IDLE STATE)]\n";
    std::cout << "  ----------------------------------------------------------------------------\n";
    std::cout << "  Sample | CPU Util | CPU Avg Clock | CPU Temp | GPU Clock | GPU Temp | GPU Power\n";
    std::cout << "  ----------------------------------------------------------------------------\n";

    for (const auto& s : samples) {
        std::cout << "    #" << std::setw(3) << s.sampleIndex << "  | "
                  << std::setw(6) << std::fixed << std::setprecision(1) << s.cpuUtilizationPercent << "% | "
                  << std::setw(7) << std::fixed << std::setprecision(0) << s.cpuCurrentAvgMhz << " MHz  | "
                  << (s.cpuTempCelsius > 0 ? std::to_string((int)s.cpuTempCelsius) + " C " : "N/A   ") << " | "
                  << std::setw(5) << s.gpuCoreClockMhz << " MHz  | "
                  << std::setw(4) << s.gpuTempCelsius << " C   | "
                  << std::setw(5) << std::fixed << std::setprecision(1) << s.gpuPowerWatts << " W\n";
    }
    std::cout << "  ----------------------------------------------------------------------------\n";

    std::cout << "\n[2. STATISTICAL BASELINE SUMMARY]\n";
    std::cout << "  ----------------------------------------------------------------------------\n";
    std::cout << "  Component & Metric         |    Average |    Minimum |    Maximum |    Std Dev\n";
    std::cout << "  ----------------------------------------------------------------------------\n";

    auto printMetric = [](const char* name, const MetricStats& m, const char* unit) {
        std::cout << "  " << std::left << std::setw(26) << name << " | "
                  << std::right << std::setw(8) << std::fixed << std::setprecision(1) << m.avgVal << " " << std::left << std::setw(3) << unit << "| "
                  << std::right << std::setw(8) << std::fixed << std::setprecision(1) << m.minVal << " " << std::left << std::setw(3) << unit << "| "
                  << std::right << std::setw(8) << std::fixed << std::setprecision(1) << m.maxVal << " " << std::left << std::setw(3) << unit << "| "
                  << std::right << std::setw(8) << std::fixed << std::setprecision(2) << m.stdDev << " " << unit << "\n";
    };

    printMetric("CPU Idle Utilization", agg.cpuUtil, "%");
    printMetric("CPU Current Frequency", agg.cpuClock, "MHz");
    printMetric("CPU Effective Frequency", agg.cpuEffectiveClock, "MHz");
    if (agg.cpuTemp.avgVal > 0.0) {
        printMetric("CPU Package Temperature", agg.cpuTemp, "C");
    }
    printMetric("GPU Core Clock (Idle)", agg.gpuClock, "MHz");
    printMetric("GPU Memory Clock", agg.gpuMemClock, "MHz");
    printMetric("GPU Temperature", agg.gpuTemp, "C");
    printMetric("GPU Power Draw", agg.gpuPower, "W");
    printMetric("GPU Core Utilization", agg.gpuUtil, "%");
    printMetric("RAM Active Allocation", agg.ramUsedMB, "MB");
    printMetric("RAM Memory Load", agg.ramLoad, "%");
    std::cout << "  ----------------------------------------------------------------------------\n";

    std::cout << "\n[3. CLOCK TERMINOLOGY & DYNAMIC FREQUENCY EXPLANATION]\n";
    std::cout << "  * Base Clock (2.7 GHz): Guaranteed steady-state frequency under all-core TDP limits (45W).\n";
    std::cout << "  * Boost Clock (up to 4.5 GHz): Opportunistic frequency for 1-2 cores governed by PL2 power.\n";
    std::cout << "  * Current Clock: The momentary multiplier state polled by the OS scheduler.\n";
    std::cout << "  * Effective Clock: Cycles executed factoring in C-state sleep intervals (Unhalted TSC / time).\n";
    std::cout << "  * Idle Clock (~300 MHz GPU / ~1.2 GHz CPU): NOT throttling! Dynamic ASPM power saving.\n";
    std::cout << "  * Sustained Clock: Equilibrium frequency maintained after fan stabilization & thermal soak.\n";

    std::cout << "\n================================================================================\n";
    std::cout << "             BASELINE READY — PROCEED TO PHASE 2 (CPU BENCHMARK)               \n";
    std::cout << "================================================================================\n\n";
}

static void SaveBaselineJson(const std::vector<BaselineSample>& samples,
                             const AggregatedBaseline& agg,
                             const std::string& filepath) {
    std::ofstream f(filepath);
    if (!f.is_open()) return;

    f << "{\n";
    f << "  \"samples_count\": " << samples.size() << ",\n";
    f << "  \"summary\": {\n";
    f << "    \"cpu_util_avg\": " << agg.cpuUtil.avgVal << ",\n";
    f << "    \"cpu_util_stddev\": " << agg.cpuUtil.stdDev << ",\n";
    f << "    \"cpu_clock_avg_mhz\": " << agg.cpuClock.avgVal << ",\n";
    f << "    \"cpu_effective_clock_avg_mhz\": " << agg.cpuEffectiveClock.avgVal << ",\n";
    f << "    \"cpu_temp_avg_c\": " << agg.cpuTemp.avgVal << ",\n";
    f << "    \"gpu_clock_avg_mhz\": " << agg.gpuClock.avgVal << ",\n";
    f << "    \"gpu_mem_clock_avg_mhz\": " << agg.gpuMemClock.avgVal << ",\n";
    f << "    \"gpu_temp_avg_c\": " << agg.gpuTemp.avgVal << ",\n";
    f << "    \"gpu_power_avg_watts\": " << agg.gpuPower.avgVal << ",\n";
    f << "    \"gpu_util_avg\": " << agg.gpuUtil.avgVal << ",\n";
    f << "    \"ram_used_avg_mb\": " << agg.ramUsedMB.avgVal << ",\n";
    f << "    \"ram_load_avg_percent\": " << agg.ramLoad.avgVal << "\n";
    f << "  },\n";
    f << "  \"samples\": [\n";

    for (size_t i = 0; i < samples.size(); ++i) {
        const auto& s = samples[i];
        f << "    {\n";
        f << "      \"index\": " << s.sampleIndex << ",\n";
        f << "      \"time_sec\": " << s.timestampSec << ",\n";
        f << "      \"cpu_util\": " << s.cpuUtilizationPercent << ",\n";
        f << "      \"cpu_clock_mhz\": " << s.cpuCurrentAvgMhz << ",\n";
        f << "      \"cpu_effective_clock_mhz\": " << s.cpuEffectiveMhz << ",\n";
        f << "      \"cpu_temp_c\": " << s.cpuTempCelsius << ",\n";
        f << "      \"gpu_clock_mhz\": " << s.gpuCoreClockMhz << ",\n";
        f << "      \"gpu_mem_clock_mhz\": " << s.gpuMemClockMhz << ",\n";
        f << "      \"gpu_temp_c\": " << s.gpuTempCelsius << ",\n";
        f << "      \"gpu_power_watts\": " << s.gpuPowerWatts << ",\n";
        f << "      \"gpu_util\": " << s.gpuCoreUtilPercent << ",\n";
        f << "      \"ram_used_mb\": " << s.ramUsedMB << ",\n";
        f << "      \"ram_load_percent\": " << s.ramLoadPercent << "\n";
        f << "    }";
        if (i + 1 < samples.size()) f << ",";
        f << "\n";
    }
    f << "  ]\n";
    f << "}\n";
    f.close();

    std::cout << "[INFO] Baseline telemetry exported to: " << filepath << "\n";
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

int main(int argc, char* argv[]) {
    int totalSamples = 5;
    int intervalMs = 1000;

    if (argc > 1) {
        totalSamples = std::atoi(argv[1]);
        if (totalSamples < 2) totalSamples = 2;
    }

    std::cout << "[INFO] Initializing system baseline calibration (" 
              << totalSamples << " samples, " << intervalMs << "ms interval)...\n";
    std::cout << "[INFO] Keep background applications calm during this test.\n\n";

    CpuMonitor cpu(12);
    NvmlMonitor gpu;

    // Warm-up initial delta
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    cpu.SampleUtilization();

    std::vector<BaselineSample> samples;
    auto startTime = std::chrono::high_resolution_clock::now();

    for (int i = 1; i <= totalSamples; ++i) {
        std::this_thread::sleep_for(std::chrono::milliseconds(intervalMs));

        BaselineSample s;
        s.sampleIndex = i;

        auto now = std::chrono::high_resolution_clock::now();
        s.timestampSec = std::chrono::duration<double>(now - startTime).count();

        // Sample CPU
        s.cpuUtilizationPercent = cpu.SampleUtilization();
        cpu.SampleClocks(s);
        s.cpuEffectiveMhz = cpu.SampleEffectiveClock(40);
        s.cpuTempCelsius = cpu.SampleTemperature();

        // Sample GPU
        gpu.Sample(s);

        // Sample RAM
        SampleRam(s);

        samples.push_back(s);

        std::cout << "  Sample [" << i << "/" << totalSamples << "] collected..." << std::endl;
    }

    AggregatedBaseline agg = ComputeAggregates(samples);
    PrintBaselineDashboard(samples, agg);
    SaveBaselineJson(samples, agg, "results/cpu_gpu_baseline.json");

    return 0;
}
