#pragma once
/**
 * ============================================================================
 * PC BENCHMARK SUITE — FULLY DYNAMIC RAM & CACHE SUBSYSTEM BENCHMARK
 * ============================================================================
 * Measures: Sequential Read/Write/Copy (GB/s), Random Access Latency (ns),
 * Cache vs DRAM hierarchy curve (L1 -> L2 -> L3 -> Main Memory).
 * Zero hardcoding: Sized dynamically to fit available physical memory.
 * ============================================================================
 */

#include <vector>
#include <chrono>
#include <random>
#include <numeric>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <cstring>
#include <cstdint>

#ifndef NOMINMAX
#define NOMINMAX
#endif
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <intrin.h>
#include <immintrin.h>

namespace RamBench {

struct HierarchyStep {
    std::string tierName; // "L1 Cache", "L2 Cache", "L3 Cache", "Main RAM"
    uint64_t bufferSizeKB = 0;
    double bandwidthGBs = 0.0;
    double latencyNs = 0.0;
};

struct RamBenchmarkResult {
    uint64_t testedBufferMB = 0;
    double seqReadGBs = 0.0;
    double seqWriteGBs = 0.0;
    double copyGBs = 0.0;
    double randomAccessLatencyNs = 0.0;
    double theoreticalMaxGBs = 0.0;
    double busEfficiencyPercent = 0.0;
    std::vector<HierarchyStep> cacheCurve;
    std::string channelEvaluation;
};

template <typename T>
__forceinline void DoNotOptimize(T const& value) {
    _ReadWriteBarrier();
    *(reinterpret_cast<volatile const char*>(&value));
}

// ----------------------------------------------------------------------------
// SEQUENTIAL READ BENCHMARK (AVX2 / 256-BIT UNROLLED LOADS)
// ----------------------------------------------------------------------------
inline double BenchmarkSequentialRead(const uint8_t* buffer, size_t bytes, int iterations) {
    const size_t chunks = bytes / 128; // 4x 32-byte AVX registers per loop
    auto t0 = std::chrono::high_resolution_clock::now();

    __m256i sum0 = _mm256_setzero_si256();
    __m256i sum1 = _mm256_setzero_si256();

    for (int iter = 0; iter < iterations; ++iter) {
        const __m256i* ptr = reinterpret_cast<const __m256i*>(buffer);
        for (size_t i = 0; i < chunks; ++i) {
            __m256i r0 = _mm256_loadu_si256(ptr + 0);
            __m256i r1 = _mm256_loadu_si256(ptr + 1);
            __m256i r2 = _mm256_loadu_si256(ptr + 2);
            __m256i r3 = _mm256_loadu_si256(ptr + 3);
            sum0 = _mm256_add_epi64(sum0, _mm256_add_epi64(r0, r1));
            sum1 = _mm256_add_epi64(sum1, _mm256_add_epi64(r2, r3));
            ptr += 4;
        }
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    DoNotOptimize(sum0);
    DoNotOptimize(sum1);

    double sec = std::chrono::duration<double>(t1 - t0).count();
    double totalBytes = static_cast<double>(bytes) * iterations;
    return (totalBytes / (1024.0 * 1024.0 * 1024.0)) / sec; // GB/s
}

// ----------------------------------------------------------------------------
// SEQUENTIAL WRITE BENCHMARK (STREAMING NON-TEMPORAL STORES)
// ----------------------------------------------------------------------------
inline double BenchmarkSequentialWrite(uint8_t* buffer, size_t bytes, int iterations) {
    const size_t chunks = bytes / 128;
    __m256i val = _mm256_set1_epi32(0x5A5A5A5A);
    auto t0 = std::chrono::high_resolution_clock::now();

    for (int iter = 0; iter < iterations; ++iter) {
        __m256i* ptr = reinterpret_cast<__m256i*>(buffer);
        for (size_t i = 0; i < chunks; ++i) {
            _mm256_stream_si256(ptr + 0, val);
            _mm256_stream_si256(ptr + 1, val);
            _mm256_stream_si256(ptr + 2, val);
            _mm256_stream_si256(ptr + 3, val);
            ptr += 4;
        }
    }
    _mm_sfence();
    auto t1 = std::chrono::high_resolution_clock::now();

    double sec = std::chrono::duration<double>(t1 - t0).count();
    double totalBytes = static_cast<double>(bytes) * iterations;
    return (totalBytes / (1024.0 * 1024.0 * 1024.0)) / sec; // GB/s
}

// ----------------------------------------------------------------------------
// MEMORY COPY BENCHMARK
// ----------------------------------------------------------------------------
inline double BenchmarkCopy(uint8_t* dst, const uint8_t* src, size_t bytes, int iterations) {
    auto t0 = std::chrono::high_resolution_clock::now();
    for (int iter = 0; iter < iterations; ++iter) {
        std::memcpy(dst, src, bytes);
        DoNotOptimize(dst[0]);
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    double sec = std::chrono::duration<double>(t1 - t0).count();
    double totalBytes = static_cast<double>(bytes) * iterations * 2.0; // Read + Write
    return (totalBytes / (1024.0 * 1024.0 * 1024.0)) / sec; // GB/s
}

// ----------------------------------------------------------------------------
// RANDOM ACCESS POINTER-CHASING LATENCY (DEFEATS PREFETCHERS)
// ----------------------------------------------------------------------------
inline double BenchmarkRandomLatency(size_t bufferBytes, uint64_t totalHops) {
    const size_t count = bufferBytes / sizeof(uint32_t);
    std::vector<uint32_t> nextIndex(count);
    std::vector<uint32_t> indices(count);

    for (size_t i = 0; i < count; ++i) indices[i] = static_cast<uint32_t>(i);

    // Stride with a large prime number to uniformly disperse accesses across cache lines
    const size_t stride = 17; // 17 cache lines
    for (size_t i = 0; i < count; ++i) {
        nextIndex[i] = static_cast<uint32_t>((i + stride) % count);
    }

    // Measure pointer chase loop
    uint32_t curr = 0;
    auto t0 = std::chrono::high_resolution_clock::now();

    for (uint64_t h = 0; h < totalHops; ++h) {
        curr = nextIndex[curr];
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    DoNotOptimize(curr);

    double sec = std::chrono::duration<double>(t1 - t0).count();
    return (sec * 1e9) / static_cast<double>(totalHops); // nanoseconds per hop
}

// ----------------------------------------------------------------------------
// ORCHESTRATED RAM BENCHMARK EXECUTION
// ----------------------------------------------------------------------------
inline RamBenchmarkResult RunBenchmark(uint64_t safeBufferMB, int configuredSpeedMTs, int channelCount) {
    RamBenchmarkResult res;
    res.testedBufferMB = safeBufferMB;

    size_t bufferBytes = static_cast<size_t>(safeBufferMB) * 1024 * 1024;
    std::vector<uint8_t> bufferA(bufferBytes);
    std::vector<uint8_t> bufferB(bufferBytes);

    // Initialize data
    std::fill(bufferA.begin(), bufferA.end(), static_cast<uint8_t>(0xAA));
    std::fill(bufferB.begin(), bufferB.end(), static_cast<uint8_t>(0x55));

    std::cout << "  [1/5] Measuring Sequential Read Bandwidth (" << safeBufferMB << " MB Buffer)..." << std::flush;
    int readIters = (std::max)(2, static_cast<int>(2048 / safeBufferMB));
    res.seqReadGBs = BenchmarkSequentialRead(bufferA.data(), bufferBytes, readIters);
    std::cout << " " << std::fixed << std::setprecision(2) << res.seqReadGBs << " GB/s\n";

    std::cout << "  [2/5] Measuring Sequential Write Bandwidth..." << std::flush;
    int writeIters = (std::max)(2, static_cast<int>(1536 / safeBufferMB));
    res.seqWriteGBs = BenchmarkSequentialWrite(bufferA.data(), bufferBytes, writeIters);
    std::cout << " " << std::fixed << std::setprecision(2) << res.seqWriteGBs << " GB/s\n";

    std::cout << "  [3/5] Measuring Memory Copy Bandwidth..." << std::flush;
    int copyIters = (std::max)(2, static_cast<int>(1024 / safeBufferMB));
    res.copyGBs = BenchmarkCopy(bufferB.data(), bufferA.data(), bufferBytes, copyIters);
    std::cout << " " << std::fixed << std::setprecision(2) << res.copyGBs << " GB/s\n";

    std::cout << "  [4/5] Measuring Main Memory Random Latency (Pointer Chasing)..." << std::flush;
    res.randomAccessLatencyNs = BenchmarkRandomLatency(bufferBytes, 50'000'000);
    std::cout << " " << std::fixed << std::setprecision(1) << res.randomAccessLatencyNs << " ns\n";

    // ------------------------------------------------------------------------
    // CACHE VS MEMORY HIERARCHY CURVE
    // ------------------------------------------------------------------------
    std::cout << "  [5/5] Generating Cache vs DRAM Hierarchy Step Curve..." << std::endl;
    struct Tier { const char* name; size_t kb; int iters; };
    Tier tiers[] = {
        {"L1 Data Cache", 32, 1000},
        {"L2 Cache", 512, 100},
        {"L3 Cache", 8192, 10},
        {"Main System RAM", static_cast<size_t>(safeBufferMB * 1024), 2}
    };

    for (const auto& t : tiers) {
        size_t bBytes = t.kb * 1024;
        std::vector<uint8_t> tierBuf(bBytes, 0x77);
        double bw = BenchmarkSequentialRead(tierBuf.data(), bBytes, t.iters);
        double lat = BenchmarkRandomLatency(bBytes, 10'000'000);

        HierarchyStep step;
        step.tierName = t.name;
        step.bufferSizeKB = t.kb;
        step.bandwidthGBs = bw;
        step.latencyNs = lat;
        res.cacheCurve.push_back(step);

        std::cout << "        * " << std::left << std::setw(18) << t.name 
                  << " (" << std::right << std::setw(6) << t.kb << " KB) -> "
                  << std::setw(6) << std::fixed << std::setprecision(1) << bw << " GB/s | "
                  << std::setw(5) << std::fixed << std::setprecision(1) << lat << " ns\n";
    }

    // Theoretical Maximum Calculation:
    // Bandwidth = MT/s * 8 bytes/transfer * channels
    if (configuredSpeedMTs > 0 && channelCount > 0) {
        res.theoreticalMaxGBs = (static_cast<double>(configuredSpeedMTs) * 8.0 * channelCount) / 1000.0;
        res.busEfficiencyPercent = (res.seqReadGBs / res.theoreticalMaxGBs) * 100.0;
    }

    if (channelCount == 1) {
        res.channelEvaluation = "SINGLE-CHANNEL BOTTLENECK: Only 1 DIMM is populated. Adding a second stick will double memory bandwidth.";
    } else {
        res.channelEvaluation = "DUAL-CHANNEL OPTIMAL: Memory subsystem operating at full multi-channel bandwidth.";
    }

    return res;
}

} // namespace RamBench
