/**
 * ============================================================================
 * PC PERFORMANCE BENCHMARK & BOTTLENECK ANALYSIS SUITE
 * PHASE 2 — CPU SINGLE-THREAD BENCHMARK
 * ============================================================================
 * 
 * Target Architecture: Intel Core i5-11400H (Tiger Lake-H, Willow Cove Core)
 * Instruction Sets: Scalar Integer/FP, FMA, AVX2, AVX-512F
 * Language: C++20 (MSVC)
 * Dependencies: Win32 APIs, Powrprof, x86 SIMD Intrinsics (<immintrin.h>)
 * 
 * Output: Terminal Report + results/cpu_single.json
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
#include <random>
#include <algorithm>
#include <cstdint>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <powrprof.h>
#include <intrin.h>
#include <immintrin.h>

#pragma comment(lib, "Powrprof.lib")

// ============================================================================
// COMPILER OPTIMIZATION INHIBITOR (PREVENTS DEAD-CODE ELIMINATION)
// ============================================================================

template <typename T>
__forceinline void DoNotOptimize(T const& value) {
    _ReadWriteBarrier();
    *(reinterpret_cast<volatile const char*>(&value));
}

// ============================================================================
// BENCHMARK RESULT DATA STRUCTURES
// ============================================================================

struct WorkloadResult {
    std::string name;
    std::string category;
    double operationsTotal = 0.0;
    std::string opUnit;

    double minTimeSec = 0.0;
    double maxTimeSec = 0.0;
    double avgTimeSec = 0.0;
    double stdDevTimeSec = 0.0;

    double opsPerSec = 0.0;
    double gflops = 0.0; // Where applicable
    double score = 0.0;
    uint32_t cpuMhzObserved = 0;
};

// ============================================================================
// CPU FREQUENCY MONITOR
// ============================================================================

struct ProcessorPowerInfo {
    ULONG number;
    ULONG maxMhz;
    ULONG currentMhz;
    ULONG mhzLimit;
    ULONG maxIdleState;
    ULONG currentIdleState;
};

static uint32_t GetCurrentCpuFrequencyMhz() {
    ProcessorPowerInfo info[12] = {0};
    LONG status = CallNtPowerInformation(ProcessorInformation, nullptr, 0, info, sizeof(info));
    if (status == 0) {
        return info[0].currentMhz;
    }
    return 0;
}

// ============================================================================
// WORKLOAD KERNELS (CAREFULLY CRAFTED INSTRUCTION LOOPS)
// ============================================================================

// ----------------------------------------------------------------------------
// A. Integer Arithmetic (64-bit ALU, Bit Shifts, Modular arithmetic)
// ----------------------------------------------------------------------------
static uint64_t BenchmarkIntegerArithmetic(size_t iterations) {
    uint64_t a = 0x9E3779B97F4A7C15ULL;
    uint64_t b = 0xBF58476D1CE4E5B9ULL;
    uint64_t c = 0x94D049BB133111EBULL;

    for (size_t i = 0; i < iterations; ++i) {
        a ^= (b + 0x517cc1b727220a95ULL + (a << 6) + (a >> 2));
        b += (c ^ (a >> 3)) * 0x9E3779B97F4A7C15ULL;
        c ^= (a + (b << 11)) + (c >> 7);
        a = (a << 13) | (a >> (64 - 13)); // Rotate left
    }
    return a ^ b ^ c;
}

// ----------------------------------------------------------------------------
// B. Floating-Point Arithmetic (Double Precision IEEE 754 Chained Operations)
// ----------------------------------------------------------------------------
static double BenchmarkFloatingPoint(size_t iterations) {
    double x = 1.0000001;
    double y = 1.0000002;
    double z = 1.0000003;
    double w = 0.9999999;

    for (size_t i = 0; i < iterations; ++i) {
        x = x * y + z - w;
        y = y * z + w - x;
        z = z * w + x - y;
        w = w * x + y - z;

        // Re-scale slightly to prevent overflow/underflow to Inf/NaN
        if (x > 1e12 || x < -1e12) {
            x *= 1e-12;
            y *= 1e-12;
            z *= 1e-12;
            w *= 1e-12;
        }
    }
    return x + y + z + w;
}

// ----------------------------------------------------------------------------
// C. Multiplication & Addition (Scalar FMA Emulation / Interleaved ALU ILP)
// ----------------------------------------------------------------------------
static float BenchmarkMulAdd(size_t iterations) {
    float a0 = 1.01f, a1 = 1.02f, a2 = 1.03f, a3 = 1.04f;
    float b0 = 0.99f, b1 = 0.98f, b2 = 0.97f, b3 = 0.96f;
    float c0 = 0.50f, c1 = 0.51f, c2 = 0.52f, c3 = 0.53f;

    for (size_t i = 0; i < iterations; ++i) {
        // 4 parallel independent dependency chains to saturate execution ports
        a0 = a0 * b0 + c0;
        a1 = a1 * b1 + c1;
        a2 = a2 * b2 + c2;
        a3 = a3 * b3 + c3;

        b0 = b0 * a0 + c0;
        b1 = b1 * a1 + c1;
        b2 = b2 * a2 + c2;
        b3 = b3 * a3 + c3;

        if (a0 > 1000.0f) {
            a0 *= 0.001f; a1 *= 0.001f; a2 *= 0.001f; a3 *= 0.001f;
            b0 *= 0.001f; b1 *= 0.001f; b2 *= 0.001f; b3 *= 0.001f;
        }
    }
    return (a0 + a1) + (a2 + a3) + (b0 + b1) + (b2 + b3);
}

// ----------------------------------------------------------------------------
// D. Transcendental Functions (sin, cos, exp, log, sqrt)
// ----------------------------------------------------------------------------
static double BenchmarkTranscendentals(size_t iterations) {
    double acc = 0.0;
    double delta = 0.000001;
    double val = 0.1;

    for (size_t i = 0; i < iterations; ++i) {
        val += delta;
        acc += std::sin(val) * std::cos(val) + std::sqrt(val) + std::log(val + 1.0);
    }
    return acc;
}

// ----------------------------------------------------------------------------
// E. Branch-Heavy Workload (Branch Prediction Stress & Collatz Dynamics)
// ----------------------------------------------------------------------------
static uint64_t BenchmarkBranchHeavy(size_t iterations) {
    uint64_t totalSteps = 0;
    // Mix deterministic pseudorandom data to stress the Branch Target Buffer (BTB)
    uint64_t state = 0x123456789ABCDEF0ULL;

    for (size_t i = 1; i <= iterations; ++i) {
        state ^= state >> 12;
        state ^= state << 25;
        state ^= state >> 27;

        uint64_t n = (state % 10000) + 1;
        while (n > 1) {
            if (n & 1) {
                n = 3 * n + 1;
            } else {
                n = n / 2;
            }
            totalSteps++;
        }
    }
    return totalSteps;
}

// ----------------------------------------------------------------------------
// F. Memory-Dependent Workload (Pointer-Chasing Latency Test in L1/L2)
// ----------------------------------------------------------------------------
static uint64_t BenchmarkMemoryDependent(size_t iterations) {
    // 32 KB array fits completely inside L1 Data Cache (48 KB on Tiger Lake)
    const size_t arraySize = 32 * 1024 / sizeof(uint32_t);
    std::vector<uint32_t> indices(arraySize);

    // Build pseudo-random permutation cycle for pointer-chasing
    for (size_t i = 0; i < arraySize; ++i) indices[i] = static_cast<uint32_t>(i);
    std::mt19937 g(42);
    std::shuffle(indices.begin(), indices.end(), g);

    std::vector<uint32_t> nextIndex(arraySize);
    for (size_t i = 0; i < arraySize - 1; ++i) {
        nextIndex[indices[i]] = indices[i + 1];
    }
    nextIndex[indices[arraySize - 1]] = indices[0];

    uint32_t curr = 0;
    for (size_t i = 0; i < iterations; ++i) {
        curr = nextIndex[curr];
    }
    return curr;
}

// ----------------------------------------------------------------------------
// G. SIMD Workload: AVX2 256-bit Vector FMA
// ----------------------------------------------------------------------------
static float BenchmarkSIMD_AVX2(size_t iterations) {
    __m256 vA = _mm256_set1_ps(1.0001f);
    __m256 vB = _mm256_set1_ps(1.0002f);
    __m256 vC = _mm256_set1_ps(0.5000f);

    for (size_t i = 0; i < iterations; ++i) {
        // 8 single-precision floats processed simultaneously per vector
        // 4 unrolled FMA operations = 32 FP32 operations per loop iteration
        vA = _mm256_fmadd_ps(vA, vB, vC);
        vB = _mm256_fmadd_ps(vB, vA, vC);
        vA = _mm256_fmadd_ps(vA, vB, vC);
        vB = _mm256_fmadd_ps(vB, vA, vC);

        // Normalize periodically
        if ((i & 0xFF) == 0) {
            vA = _mm256_mul_ps(vA, _mm256_set1_ps(0.5f));
            vB = _mm256_mul_ps(vB, _mm256_set1_ps(0.5f));
        }
    }

    alignas(32) float result[8];
    _mm256_store_ps(result, _mm256_add_ps(vA, vB));
    return result[0] + result[1] + result[2] + result[3];
}

// ----------------------------------------------------------------------------
// G2. SIMD Workload: AVX-512F 512-bit Vector FMA
// ----------------------------------------------------------------------------
static float BenchmarkSIMD_AVX512(size_t iterations) {
    __m512 vA = _mm512_set1_ps(1.0001f);
    __m512 vB = _mm512_set1_ps(1.0002f);
    __m512 vC = _mm512_set1_ps(0.5000f);

    for (size_t i = 0; i < iterations; ++i) {
        // 16 single-precision floats processed simultaneously per 512-bit vector
        // 4 unrolled FMA operations = 64 FP32 operations per loop iteration
        vA = _mm512_fmadd_ps(vA, vB, vC);
        vB = _mm512_fmadd_ps(vB, vA, vC);
        vA = _mm512_fmadd_ps(vA, vB, vC);
        vB = _mm512_fmadd_ps(vB, vA, vC);

        if ((i & 0xFF) == 0) {
            vA = _mm512_mul_ps(vA, _mm512_set1_ps(0.5f));
            vB = _mm512_mul_ps(vB, _mm512_set1_ps(0.5f));
        }
    }

    alignas(64) float result[16];
    _mm512_store_ps(result, _mm512_add_ps(vA, vB));
    return result[0] + result[1] + result[2] + result[3];
}

// ============================================================================
// HARNESS EXECUTION & STATISTICAL ANALYSIS
// ============================================================================

template <typename Func>
WorkloadResult RunWorkload(const std::string& name,
                            const std::string& category,
                            double opsPerIteration,
                            const std::string& opUnit,
                            size_t iterations,
                            int repetitions,
                            Func&& func,
                            bool computeGflops = false) {
    WorkloadResult r;
    r.name = name;
    r.category = category;
    r.opUnit = opUnit;
    r.operationsTotal = opsPerIteration * iterations;

    // 1. Warm-up pass (prime caches, spin CPU up from idle P-states)
    auto warmVal = func(iterations / 10);
    DoNotOptimize(warmVal);

    std::vector<double> timings;
    timings.reserve(repetitions);

    uint32_t mhzSample = 0;

    for (int rep = 0; rep < repetitions; ++rep) {
        auto t0 = std::chrono::high_resolution_clock::now();

        auto res = func(iterations);
        DoNotOptimize(res);

        auto t1 = std::chrono::high_resolution_clock::now();
        double elapsed = std::chrono::duration<double>(t1 - t0).count();
        timings.push_back(elapsed);

        if (rep == 0) {
            mhzSample = GetCurrentCpuFrequencyMhz();
        }
    }

    r.cpuMhzObserved = mhzSample;
    r.minTimeSec = *std::min_element(timings.begin(), timings.end());
    r.maxTimeSec = *std::max_element(timings.begin(), timings.end());

    double sum = std::accumulate(timings.begin(), timings.end(), 0.0);
    r.avgTimeSec = sum / repetitions;

    double varSum = 0.0;
    for (double t : timings) {
        varSum += (t - r.avgTimeSec) * (t - r.avgTimeSec);
    }
    r.stdDevTimeSec = std::sqrt(varSum / repetitions);

    r.opsPerSec = r.operationsTotal / r.avgTimeSec;
    if (computeGflops) {
        r.gflops = r.opsPerSec / 1e9;
    }

    // Normalized Score (operations per second / 1,000,000)
    r.score = r.opsPerSec / 1e6;

    return r;
}

// ============================================================================
// TERMINAL DASHBOARD & JSON EXPORT
// ============================================================================

static void PrintResultsTable(const std::vector<WorkloadResult>& results) {
    std::cout << "\n========================================================================================\n";
    std::cout << "                 PHASE 2: CPU SINGLE-THREAD BENCHMARK REPORT                            \n";
    std::cout << "========================================================================================\n";

    std::cout << "\n  Workload Name              | Category | Avg Time | Throughput         | GFLOPS | Score   \n";
    std::cout << "  ---------------------------+----------+----------+--------------------+--------+---------\n";

    for (const auto& r : results) {
        std::stringstream ssThroughput;
        if (r.opsPerSec >= 1e9) {
            ssThroughput << std::fixed << std::setprecision(2) << (r.opsPerSec / 1e9) << " G" << r.opUnit << "/s";
        } else if (r.opsPerSec >= 1e6) {
            ssThroughput << std::fixed << std::setprecision(2) << (r.opsPerSec / 1e6) << " M" << r.opUnit << "/s";
        } else {
            ssThroughput << std::fixed << std::setprecision(0) << r.opsPerSec << " " << r.opUnit << "/s";
        }

        std::cout << "  " << std::left << std::setw(26) << r.name << " | "
                  << std::left << std::setw(8) << r.category << " | "
                  << std::right << std::setw(6) << std::fixed << std::setprecision(3) << r.avgTimeSec << " s | "
                  << std::right << std::setw(18) << ssThroughput.str() << " | ";

        if (r.gflops > 0.0) {
            std::cout << std::right << std::setw(6) << std::fixed << std::setprecision(1) << r.gflops << " | ";
        } else {
            std::cout << "  N/A  | ";
        }

        std::cout << std::right << std::setw(7) << std::fixed << std::setprecision(1) << r.score << "\n";
    }

    std::cout << "  ----------------------------------------------------------------------------------------\n";
    std::cout << "\n  [VARIANCE & TIMING CONSISTENCY]\n";
    for (const auto& r : results) {
        double cv = (r.avgTimeSec > 0.0) ? (r.stdDevTimeSec / r.avgTimeSec) * 100.0 : 0.0;
        std::cout << "  * " << std::left << std::setw(26) << r.name 
                  << " -> Min: " << std::fixed << std::setprecision(4) << r.minTimeSec << "s"
                  << ", Max: " << r.maxTimeSec << "s"
                  << ", StdDev: " << r.stdDevTimeSec << "s"
                  << " (CV: " << std::setprecision(2) << cv << "%, Active Clock: " << r.cpuMhzObserved << " MHz)\n";
    }
    std::cout << "\n========================================================================================\n";
}

static void SaveJson(const std::vector<WorkloadResult>& results, const std::string& filepath) {
    std::ofstream f(filepath);
    if (!f.is_open()) return;

    f << "{\n";
    f << "  \"timestamp\": \"" << __DATE__ << " " << __TIME__ << "\",\n";
    f << "  \"cpu\": \"Intel Core i5-11400H\",\n";
    f << "  \"thread_count\": 1,\n";
    f << "  \"workloads\": [\n";

    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        f << "    {\n";
        f << "      \"name\": \"" << r.name << "\",\n";
        f << "      \"category\": \"" << r.category << "\",\n";
        f << "      \"avg_time_sec\": " << r.avgTimeSec << ",\n";
        f << "      \"min_time_sec\": " << r.minTimeSec << ",\n";
        f << "      \"max_time_sec\": " << r.maxTimeSec << ",\n";
        f << "      \"std_dev_sec\": " << r.stdDevTimeSec << ",\n";
        f << "      \"ops_per_sec\": " << r.opsPerSec << ",\n";
        f << "      \"gflops\": " << r.gflops << ",\n";
        f << "      \"score\": " << r.score << ",\n";
        f << "      \"active_clock_mhz\": " << r.cpuMhzObserved << "\n";
        f << "    }";
        if (i + 1 < results.size()) f << ",";
        f << "\n";
    }
    f << "  ]\n";
    f << "}\n";
    f.close();
    std::cout << "[INFO] Results exported to: " << filepath << "\n";
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

int main() {
    // Bind benchmark execution thread to Physical Core 0 to eliminate scheduler migration jitter
    HANDLE thread = GetCurrentThread();
    DWORD_PTR affinityMask = 1; // Logical core 0
    SetThreadAffinityMask(thread, affinityMask);

    // Set process priority to HIGH to minimize OS background interference
    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);

    std::cout << "[INFO] Thread pinned to Core 0 (High Priority). Warmup in progress...\n\n";

    std::vector<WorkloadResult> results;
    const int REPETITIONS = 5;

    std::cout << "  [1/8] Running A. Integer Arithmetic (64-bit ALU & Bitops)..." << std::endl;
    results.push_back(RunWorkload("Integer Arithmetic", "ALU", 12.0, "Ops", 80'000'000, REPETITIONS,
                                  BenchmarkIntegerArithmetic, false));

    std::cout << "  [2/8] Running B. Floating-Point Arithmetic (FP64 Chained)..." << std::endl;
    results.push_back(RunWorkload("Floating-Point FP64", "FPU", 8.0, "FLOPs", 60'000'000, REPETITIONS,
                                  BenchmarkFloatingPoint, true));

    std::cout << "  [3/8] Running C. Multiplication & Addition (Scalar ILP)..." << std::endl;
    results.push_back(RunWorkload("Mul/Add Interleaved", "FPU", 16.0, "FLOPs", 50'000'000, REPETITIONS,
                                  BenchmarkMulAdd, true));

    std::cout << "  [4/8] Running D. Transcendental Functions (sin/cos/exp)..." << std::endl;
    results.push_back(RunWorkload("Transcendentals", "MATH", 4.0, "Funcs", 15'000'000, REPETITIONS,
                                  BenchmarkTranscendentals, false));

    std::cout << "  [5/8] Running E. Branch-Heavy Workload (Collatz/BTB)..." << std::endl;
    results.push_back(RunWorkload("Branch-Heavy (BTB)", "BRANCH", 10.0, "Branches", 4'000'000, REPETITIONS,
                                  BenchmarkBranchHeavy, false));

    std::cout << "  [6/8] Running F. Memory-Dependent Workload (Pointer Chasing)..." << std::endl;
    results.push_back(RunWorkload("Memory Latency (L1)", "CACHE", 1.0, "Loads", 100'000'000, REPETITIONS,
                                  BenchmarkMemoryDependent, false));

    std::cout << "  [7/8] Running G. SIMD AVX2 256-bit Vector FMA..." << std::endl;
    results.push_back(RunWorkload("SIMD AVX2 (256-bit)", "AVX2", 64.0, "FLOPs", 40'000'000, REPETITIONS,
                                  BenchmarkSIMD_AVX2, true));

    std::cout << "  [8/8] Running H. SIMD AVX-512 512-bit Vector FMA..." << std::endl;
    results.push_back(RunWorkload("SIMD AVX-512 (512-bit)", "AVX-512", 128.0, "FLOPs", 40'000'000, REPETITIONS,
                                  BenchmarkSIMD_AVX512, true));

    PrintResultsTable(results);
    SaveJson(results, "results/cpu_single.json");

    return 0;
}
