/**
 * ============================================================================
 * PC PERFORMANCE BENCHMARK & BOTTLENECK ANALYSIS SUITE
 * PHASE 4 — CPU SUSTAINED LOAD & THERMAL/POWER THROTTLING
 * ============================================================================
 * 
 * Target Platform: Windows 10/11 x64
 * Primary Hardware: Intel Core i5-11400H (6 Cores / 12 Threads)
 * Language: C++20 (MSVC)
 * Multi-threading: OpenMP (/openmp)
 * Dependencies: Win32 APIs, Powrprof, WMI (COM), OpenMP
 * 
 * Safety Features:
 *   - Automatic Emergency Thermal Cutoff (Default: 95°C, configurable)
 *   - Graceful Ctrl+C Break Handler
 *   - Non-destructive stress loops
 * 
 * Output: Terminal Timeline + results/cpu_sustained.json
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
#include <atomic>
#include <csignal>
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

// Global atomic flag for clean abort (Ctrl+C or Thermal Limit)
static std::atomic<bool> g_stopRequested{false};
static std::atomic<bool> g_thermalAbortTriggered{false};
static double g_emergencyTempLimitC = 95.0; // TjMax for i5-11400H is 100°C

// Windows Ctrl+C Handler
static BOOL WINAPI ConsoleHandler(DWORD signal) {
    if (signal == CTRL_C_EVENT || signal == CTRL_BREAK_EVENT) {
        std::cout << "\n[SAFETY] Interrupt signal received! Gracefully halting benchmark...\n";
        g_stopRequested.store(true);
        return TRUE;
    }
    return FALSE;
}

// ============================================================================
// TELEMETRY SAMPLING STRUCTURES
// ============================================================================

struct TimelineSample {
    double timestampSec = 0.0;
    double throughputGflops = 0.0;
    double cpuUtilizationPercent = 0.0;
    double cpuFrequencyMhz = 0.0;
    double cpuTemperatureCelsius = 0.0;
    uint64_t opsCompletedInWindow = 0;
};

struct SustainedSummary {
    int durationRequestedSec = 0;
    double actualDurationSec = 0.0;
    int threadCount = 12;

    double peakThroughputGflops = 0.0;
    double sustainedThroughputGflops = 0.0;
    double performanceDropPercent = 0.0;

    double peakTempC = 0.0;
    double sustainedTempC = 0.0;
    double peakFreqMhz = 0.0;
    double sustainedFreqMhz = 0.0;

    std::string throttlingClassification;
};

// ============================================================================
// SYSTEM TELEMETRY MONITOR (WINDOWS WMI + TSC + PERFORMANCE COUNTERS)
// ============================================================================

static uint64_t FileTimeToUInt64(const FILETIME& ft) {
    return (static_cast<uint64_t>(ft.dwHighDateTime) << 32) | ft.dwLowDateTime;
}

class SystemMonitor {
private:
    uint64_t prevIdle = 0;
    uint64_t prevKernel = 0;
    uint64_t prevUser = 0;

    IWbemServices* pSvc = nullptr;
    IWbemLocator* pLoc = nullptr;
    bool wmiReady = false;

public:
    SystemMonitor() {
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

    ~SystemMonitor() {
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

        uint64_t dIdle = nowIdle - prevIdle;
        uint64_t dKernel = nowKernel - prevKernel;
        uint64_t dUser = nowUser - prevUser;

        prevIdle = nowIdle;
        prevKernel = nowKernel;
        prevUser = nowUser;

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

        double targetSec = 0.025; // 25ms spin
        double elapsedSec = 0.0;
        do {
            QueryPerformanceCounter(&qpcEnd);
            elapsedSec = static_cast<double>(qpcEnd.QuadPart - qpcStart.QuadPart) / qpcFreq.QuadPart;
        } while (elapsedSec < targetSec);

        uint64_t tscEnd = __rdtsc();
        double measuredHz = static_cast<double>(tscEnd - tscStart) / elapsedSec;
        return measuredHz / 1e6;
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
                        uint32_t rawKelvin = vtProp.uintVal;
                        if (rawKelvin > 2730) {
                            tempC = (rawKelvin - 2732) / 10.0;
                        } else if (rawKelvin > 200 && rawKelvin < 400) {
                            tempC = rawKelvin - 273.15;
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
// CONTINUOUS COMPUTE WORKER (FMA NUMERICAL SYNTHESIS)
// ============================================================================

static void ComputeChunk(int64_t iterations, double& sink) {
    double a0 = 1.000001, a1 = 1.000002;
    double b0 = 0.999999, b1 = 0.999998;
    double c0 = 0.500001, c1 = 0.500002;

    for (int64_t i = 0; i < iterations; ++i) {
        // 16 operations per iteration
        a0 = a0 * b0 + c0;
        a1 = a1 * b1 + c1;
        b0 = b0 * a0 + c0;
        b1 = b1 * a1 + c1;

        if (a0 > 1000.0) {
            a0 *= 0.001; a1 *= 0.001;
            b0 *= 0.001; b1 *= 0.001;
        }
    }
    sink = a0 + a1 + b0 + b1;
}

// ============================================================================
// TIMELINE DASHBOARD & TELEMETRY SERIALIZATION
// ============================================================================

static void PrintSummary(const SustainedSummary& sum) {
    std::cout << "\n==================================================================================================\n";
    std::cout << "                      PHASE 4: CPU SUSTAINED LOAD & THROTTLING REPORT                             \n";
    std::cout << "==================================================================================================\n";
    std::cout << " Duration Tested:          " << std::fixed << std::setprecision(1) << sum.actualDurationSec << " s"
              << " (" << sum.durationRequestedSec << " s requested)\n";
    std::cout << " Active Threads:           " << sum.threadCount << " (All Physical Cores + SMT Threads)\n";
    std::cout << " Emergency Temp Cutoff:    " << g_emergencyTempLimitC << " °C\n";
    std::cout << " Emergency Abort Fired:    " << (g_thermalAbortTriggered.load() ? "[YES - CUTOFF EXCEEDED]" : "[NO - SAFE]") << "\n";
    std::cout << "--------------------------------------------------------------------------------------------------\n";
    std::cout << " Peak Initial Throughput:  " << std::fixed << std::setprecision(2) << sum.peakThroughputGflops << " GFLOPs (PL2 Turbo Window)\n";
    std::cout << " Sustained Throughput:     " << std::fixed << std::setprecision(2) << sum.sustainedThroughputGflops << " GFLOPs (Steady State)\n";
    std::cout << " Performance Degradation:  " << std::fixed << std::setprecision(1) << sum.performanceDropPercent << " %\n";
    std::cout << " Peak Temperature:         " << std::fixed << std::setprecision(1) << sum.peakTempC << " °C\n";
    std::cout << " Sustained Temperature:    " << std::fixed << std::setprecision(1) << sum.sustainedTempC << " °C\n";
    std::cout << " Peak Frequency:           " << std::fixed << std::setprecision(0) << sum.peakFreqMhz << " MHz\n";
    std::cout << " Sustained Frequency:      " << std::fixed << std::setprecision(0) << sum.sustainedFreqMhz << " MHz\n";
    std::cout << "--------------------------------------------------------------------------------------------------\n";
    std::cout << " LIKELY LIMITING FACTOR:   [" << sum.throttlingClassification << "]\n";
    std::cout << "==================================================================================================\n";
}

static void SaveJson(const std::vector<TimelineSample>& timeline,
                     const SustainedSummary& sum,
                     const std::string& filepath) {
    std::ofstream f(filepath);
    if (!f.is_open()) return;

    f << "{\n";
    f << "  \"timestamp\": \"" << __DATE__ << " " << __TIME__ << "\",\n";
    f << "  \"summary\": {\n";
    f << "    \"duration_requested_sec\": " << sum.durationRequestedSec << ",\n";
    f << "    \"actual_duration_sec\": " << sum.actualDurationSec << ",\n";
    f << "    \"threads\": " << sum.threadCount << ",\n";
    f << "    \"peak_throughput_gflops\": " << sum.peakThroughputGflops << ",\n";
    f << "    \"sustained_throughput_gflops\": " << sum.sustainedThroughputGflops << ",\n";
    f << "    \"performance_drop_percent\": " << sum.performanceDropPercent << ",\n";
    f << "    \"peak_temp_c\": " << sum.peakTempC << ",\n";
    f << "    \"sustained_temp_c\": " << sum.sustainedTempC << ",\n";
    f << "    \"peak_freq_mhz\": " << sum.peakFreqMhz << ",\n";
    f << "    \"sustained_freq_mhz\": " << sum.sustainedFreqMhz << ",\n";
    f << "    \"limiting_factor\": \"" << sum.throttlingClassification << "\"\n";
    f << "  },\n";
    f << "  \"timeline\": [\n";

    for (size_t i = 0; i < timeline.size(); ++i) {
        const auto& s = timeline[i];
        f << "    {\n";
        f << "      \"time_sec\": " << s.timestampSec << ",\n";
        f << "      \"throughput_gflops\": " << s.throughputGflops << ",\n";
        f << "      \"cpu_utilization\": " << s.cpuUtilizationPercent << ",\n";
        f << "      \"cpu_frequency_mhz\": " << s.cpuFrequencyMhz << ",\n";
        f << "      \"cpu_temperature_c\": " << s.cpuTemperatureCelsius << "\n";
        f << "    }";
        if (i + 1 < timeline.size()) f << ",";
        f << "\n";
    }
    f << "  ]\n";
    f << "}\n";
    f.close();
    std::cout << "[INFO] Sustained telemetry exported to: " << filepath << "\n";
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

int main(int argc, char* argv[]) {
    // Default duration: 60 seconds (Configurable to 300s or 600s)
    int testDurationSec = 60;
    if (argc > 1) {
        testDurationSec = std::atoi(argv[1]);
        if (testDurationSec < 10) testDurationSec = 10;
    }

    if (argc > 2) {
        g_emergencyTempLimitC = std::atof(argv[2]);
        if (g_emergencyTempLimitC < 75.0) g_emergencyTempLimitC = 75.0;
        if (g_emergencyTempLimitC > 100.0) g_emergencyTempLimitC = 100.0;
    }

    // Register Windows console interrupt handler for Ctrl+C
    SetConsoleCtrlHandler(ConsoleHandler, TRUE);

    std::cout << "=======================================================================\n";
    std::cout << "   PC BENCHMARK SUITE — PHASE 4: CPU SUSTAINED LOAD TEST\n";
    std::cout << "=======================================================================\n";
    std::cout << " Target Duration:     " << testDurationSec << " seconds\n";
    std::cout << " Emergency Temp Cap:  " << g_emergencyTempLimitC << " °C\n";
    std::cout << " Active Threads:      12 (Full Tiger Lake-H Core All-Out Stress)\n";
    std::cout << " Press Ctrl+C at any time to trigger a graceful emergency abort.\n\n";

    SystemMonitor monitor;
    omp_set_num_threads(12);

    std::vector<TimelineSample> timeline;
    std::atomic<uint64_t> totalOperationsInWindow{0};

    auto testStartTime = std::chrono::high_resolution_clock::now();
    auto nextSampleTime = testStartTime + std::chrono::seconds(1);

    std::cout << "  Time (s) | Throughput  | CPU Util | Active Freq | CPU Temp | Status\n";
    std::cout << "  ---------+-------------+----------+-------------+----------+---------------------\n";

    // Launch worker threads in OpenMP parallel region
    #pragma omp parallel
    {
        double sink = 0.0;
        const int64_t chunkSize = 1'000'000; // 1M iterations = 16M FLOPs
        while (!g_stopRequested.load()) {
            ComputeChunk(chunkSize, sink);
            totalOperationsInWindow.fetch_add(chunkSize * 16);

            // Master thread coordinates 1-second sampling timeline & safety checks
            #pragma omp master
            {
                auto now = std::chrono::high_resolution_clock::now();
                if (now >= nextSampleTime) {
                    double elapsedTotal = std::chrono::duration<double>(now - testStartTime).count();

                    uint64_t opsDone = totalOperationsInWindow.exchange(0);
                    double gflops = (static_cast<double>(opsDone) / 1e9) / 1.0; // Per 1-second window

                    double util = monitor.SampleUtilization();
                    double freq = monitor.MeasureActiveFrequencyMhz();
                    double temp = monitor.SampleTemperature();

                    TimelineSample sample;
                    sample.timestampSec = elapsedTotal;
                    sample.throughputGflops = gflops;
                    sample.cpuUtilizationPercent = util;
                    sample.cpuFrequencyMhz = freq;
                    sample.cpuTemperatureCelsius = temp;
                    sample.opsCompletedInWindow = opsDone;
                    timeline.push_back(sample);

                    std::string statusTag = "[NORMAL]";
                    if (temp >= g_emergencyTempLimitC) {
                        statusTag = "[EMERGENCY THERMAL CUTOFF!]";
                        g_thermalAbortTriggered.store(true);
                        g_stopRequested.store(true);
                    } else if (temp >= 90.0) {
                        statusTag = "[HIGH TEMP WARNING]";
                    } else if (gflops > 0.0) {
                        statusTag = "[SUSTAINED]";
                    }

                    std::cout << "    " << std::setw(4) << std::fixed << std::setprecision(0) << elapsedTotal << " s | "
                              << std::setw(7) << std::fixed << std::setprecision(2) << gflops << " GFLOPs | "
                              << std::setw(6) << std::fixed << std::setprecision(1) << util << "% | "
                              << std::setw(8) << std::fixed << std::setprecision(0) << freq << " MHz | "
                              << std::setw(4) << (int)temp << " C   | " << statusTag << std::endl;

                    nextSampleTime = now + std::chrono::seconds(1);

                    if (elapsedTotal >= testDurationSec) {
                        g_stopRequested.store(true);
                    }
                }
            }
        }
    }

    auto testEndTime = std::chrono::high_resolution_clock::now();
    double totalElapsedSec = std::chrono::duration<double>(testEndTime - testStartTime).count();

    // Compute Summary & Degradation
    SustainedSummary sum;
    sum.durationRequestedSec = testDurationSec;
    sum.actualDurationSec = totalElapsedSec;
    sum.threadCount = 12;

    if (!timeline.empty()) {
        // Peak is highest observed in first 10 seconds
        size_t initialWindow = std::min<size_t>(timeline.size(), 10);
        double maxInitGflops = 0.0;
        for (size_t i = 0; i < initialWindow; ++i) {
            if (timeline[i].throughputGflops > maxInitGflops) {
                maxInitGflops = timeline[i].throughputGflops;
            }
            if (timeline[i].cpuTemperatureCelsius > sum.peakTempC) {
                sum.peakTempC = timeline[i].cpuTemperatureCelsius;
            }
            if (timeline[i].cpuFrequencyMhz > sum.peakFreqMhz) {
                sum.peakFreqMhz = timeline[i].cpuFrequencyMhz;
            }
        }
        sum.peakThroughputGflops = maxInitGflops;

        // Sustained is average of last 30% of timeline
        size_t sustainedStart = timeline.size() > 5 ? (timeline.size() * 7 / 10) : 0;
        double sumSustainedGflops = 0.0;
        double sumSustainedTemp = 0.0;
        double sumSustainedFreq = 0.0;
        size_t sustainedCount = timeline.size() - sustainedStart;

        for (size_t i = sustainedStart; i < timeline.size(); ++i) {
            sumSustainedGflops += timeline[i].throughputGflops;
            sumSustainedTemp += timeline[i].cpuTemperatureCelsius;
            sumSustainedFreq += timeline[i].cpuFrequencyMhz;
        }

        sum.sustainedThroughputGflops = sumSustainedGflops / sustainedCount;
        sum.sustainedTempC = sumSustainedTemp / sustainedCount;
        sum.sustainedFreqMhz = sumSustainedFreq / sustainedCount;

        if (sum.peakThroughputGflops > 0.0) {
            sum.performanceDropPercent = ((sum.peakThroughputGflops - sum.sustainedThroughputGflops) / sum.peakThroughputGflops) * 100.0;
            if (sum.performanceDropPercent < 0.0) sum.performanceDropPercent = 0.0;
        }

        // Bottleneck Classification
        if (g_thermalAbortTriggered.load() || sum.sustainedTempC >= 92.0) {
            sum.throttlingClassification = "CPU THERMAL LIMIT (Cooling solution saturated at TjMax threshold)";
        } else if (sum.performanceDropPercent > 10.0 && sum.sustainedTempC < 85.0) {
            sum.throttlingClassification = "CPU POWER LIMIT (PL1/PL2 duration timeout, safe thermal headroom remains)";
        } else if (sum.performanceDropPercent <= 10.0) {
            sum.throttlingClassification = "STABLE / HIGH CONSISTENCY (Cooling & power delivery successfully sustain load)";
        } else {
            sum.throttlingClassification = "COMBINED THERMAL & POWER EQUILIBRIUM";
        }
    }

    PrintSummary(sum);
    SaveJson(timeline, sum, "results/cpu_sustained.json");

    return 0;
}
