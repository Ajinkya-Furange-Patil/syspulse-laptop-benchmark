#pragma once
/**
 * ============================================================================
 * PC BENCHMARK SUITE — CUDA AI & GAMING BENCHMARK SPECIFICATIONS
 * ============================================================================
 * Header interface for native CUDA kernels (SGEMM, GELU, VRAM bandwidth,
 * AI model ceiling estimation, and CPU+GPU combined stress).
 * ============================================================================
 */

#include <string>
#include <vector>
#include <cstdint>

struct CudaAiBenchmarkResult {
    bool cudaAvailable = false;
    std::string deviceName;
    int smCount = 0;
    int cudaCores = 0;
    uint64_t vramTotalMB = 0;
    uint64_t vramFreeMB = 0;

    // AI Compute Metrics
    double sgemmComputeTflops = 0.0;
    double sgemmExecutionTimeMs = 0.0;
    double geluThroughputGflops = 0.0;
    double geluMemoryBandwidthGBs = 0.0;

    // Memory Bandwidth Metrics
    double vramReadBandwidthGBs = 0.0;
    double vramWriteBandwidthGBs = 0.0;
    double vramCopyBandwidthGBs = 0.0;
    double theoreticalVramBandwidthGBs = 0.0;
    double vramEfficiencyPercent = 0.0;

    // AI Model Training & Inference Ceiling Assessment
    std::string maxInferenceModelSupported; // e.g. "Llama-3-8B Q4_K_M (Fits in 4GB VRAM)"
    std::string maxFineTuningSupported;     // e.g. "LoRA on <= 1B parameter models only"
    std::string aiSuitabilityVerdict;

    // Gaming Simulation Metrics
    double shaderComputeTflops = 0.0;
    std::string gamingTierVerdict; // "1080p Esports / 1080p Medium AAA"

    // Combined CPU+GPU Simultaneous Load Results
    double cpuIsolatedGflops = 0.0;
    double cpuCombinedGflops = 0.0;
    double gpuIsolatedTflops = 0.0;
    double gpuCombinedTflops = 0.0;
    double cpuCrossThrottlePercent = 0.0;
    double gpuCrossThrottlePercent = 0.0;
    std::string sharedPowerBudgetVerdict;
};

bool CudaCheckAvailability();
CudaAiBenchmarkResult RunCudaBenchmarks(int matrixDim, int durationSeconds, double cpuSoloGflops);
