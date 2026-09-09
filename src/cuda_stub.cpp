/**
 * ============================================================================
 * PC BENCHMARK SUITE — CUDA STUB IMPLEMENTATION (NON-CUDA / HOST FALLBACK)
 * ============================================================================
 * Enables the benchmark suite to be compiled and run seamlessly on systems
 * without an NVIDIA GPU or without the CUDA Toolkit installed (e.g., AMD,
 * Intel Iris Xe, or non-accelerated systems).
 * ============================================================================
 */

#include "cuda_bench.cuh"
#include <iostream>

bool CudaCheckAvailability() {
    // CUDA Toolkit was not linked during this build or no CUDA hardware present.
    return false;
}

CudaAiBenchmarkResult RunCudaBenchmarks(int matrixDim, int durationSeconds, double cpuSoloGflops) {
    (void)matrixDim;
    (void)durationSeconds;

    CudaAiBenchmarkResult res;
    res.cudaAvailable = false;
    res.deviceName = "N/A (Built without CUDA or no NVIDIA GPU detected)";
    res.smCount = 0;
    res.cudaCores = 0;
    res.vramTotalMB = 0;
    res.vramFreeMB = 0;

    res.sgemmComputeTflops = 0.0;
    res.sgemmExecutionTimeMs = 0.0;
    res.geluThroughputGflops = 0.0;
    res.geluMemoryBandwidthGBs = 0.0;

    res.vramReadBandwidthGBs = 0.0;
    res.vramWriteBandwidthGBs = 0.0;
    res.vramCopyBandwidthGBs = 0.0;
    res.theoreticalVramBandwidthGBs = 0.0;
    res.vramEfficiencyPercent = 0.0;

    res.maxInferenceModelSupported = "CPU-Only (Ollama / Llama.cpp CPU quantized)";
    res.maxFineTuningSupported = "NOT SUPPORTED (No CUDA GPU detected)";
    res.aiSuitabilityVerdict = "CPU / Integrated Graphics Only (Use GGUF / ONNX CPU Runtime)";

    res.shaderComputeTflops = 0.0;
    res.gamingTierVerdict = "Integrated / Non-CUDA Graphics";

    res.cpuIsolatedGflops = cpuSoloGflops;
    res.cpuCombinedGflops = cpuSoloGflops;
    res.gpuIsolatedTflops = 0.0;
    res.gpuCombinedTflops = 0.0;
    res.cpuCrossThrottlePercent = 0.0;
    res.gpuCrossThrottlePercent = 0.0;
    res.sharedPowerBudgetVerdict = "N/A: Single component (CPU-only) load tested.";

    return res;
}
