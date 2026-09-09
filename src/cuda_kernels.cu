/**
 * ============================================================================
 * PC BENCHMARK SUITE — NATIVE CUDA KERNELS FOR AI & GAMING EVALUATION
 * ============================================================================
 * Implements: Tiled Matrix Multiplication (SGEMM for Deep Learning),
 * Vector Activation (GELU), VRAM Bandwidth, Shader Simulation, and
 * Combined Simultaneous CPU+GPU Cross-Throttling Stress.
 * ============================================================================
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <iostream>
#include <iomanip>
#include <vector>
#include <chrono>
#include <cmath>
#include <string>
#include <sstream>
#include <omp.h>
#include "cuda_bench.cuh"

#define CUDA_CHECK(call) do { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { \
        std::cerr << "[CUDA ERROR] " << cudaGetErrorString(err) \
                  << " at " << __FILE__ << ":" << __LINE__ << std::endl; \
    } \
} while(0)

#define TILE_SIZE 16

// ----------------------------------------------------------------------------
// 1. AI MATRIX MULTIPLICATION (TILED SGEMM WITH SHARED MEMORY)
// ----------------------------------------------------------------------------
__global__ void sgemm_tiled_kernel(const float* __restrict__ A,
                                   const float* __restrict__ B,
                                   float* __restrict__ C,
                                   int N) {
    __shared__ float sA[TILE_SIZE][TILE_SIZE];
    __shared__ float sB[TILE_SIZE][TILE_SIZE];

    int row = blockIdx.y * TILE_SIZE + threadIdx.y;
    int col = blockIdx.x * TILE_SIZE + threadIdx.x;
    float sum = 0.0f;

    for (int t = 0; t < (N + TILE_SIZE - 1) / TILE_SIZE; ++t) {
        if (row < N && (t * TILE_SIZE + threadIdx.x) < N) {
            sA[threadIdx.y][threadIdx.x] = A[row * N + (t * TILE_SIZE + threadIdx.x)];
        } else {
            sA[threadIdx.y][threadIdx.x] = 0.0f;
        }

        if (col < N && (t * TILE_SIZE + threadIdx.y) < N) {
            sB[threadIdx.y][threadIdx.x] = B[(t * TILE_SIZE + threadIdx.y) * N + col];
        } else {
            sB[threadIdx.y][threadIdx.x] = 0.0f;
        }

        __syncthreads();

        #pragma unroll
        for (int k = 0; k < TILE_SIZE; ++k) {
            sum += sA[threadIdx.y][k] * sB[k][threadIdx.x];
        }

        __syncthreads();
    }

    if (row < N && col < N) {
        C[row * N + col] = sum;
    }
}

// ----------------------------------------------------------------------------
// 2. AI ACTIVATION FUNCTION (GELU — GAUSSIAN ERROR LINEAR UNIT)
// ----------------------------------------------------------------------------
__global__ void gelu_activation_kernel(const float4* __restrict__ in,
                                      float4* __restrict__ out,
                                      int numVec4) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < numVec4) {
        float4 v = in[idx];
        const float c1 = 0.79788456f; // sqrt(2/pi)
        const float c2 = 0.044715f;

        auto gelu_elem = [=](float x) -> float {
            float inner = c1 * (x + c2 * x * x * x);
            return 0.5f * x * (1.0f + tanhf(inner));
        };

        float4 r;
        r.x = gelu_elem(v.x);
        r.y = gelu_elem(v.y);
        r.z = gelu_elem(v.z);
        r.w = gelu_elem(v.w);
        out[idx] = r;
    }
}

// ----------------------------------------------------------------------------
// 3. VRAM GLOBAL MEMORY READ BANDWIDTH KERNEL
// ----------------------------------------------------------------------------
__global__ void vram_read_kernel(const float4* __restrict__ in,
                                float4* __restrict__ outSink,
                                int numVec4) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    float4 acc = make_float4(0.0f, 0.0f, 0.0f, 0.0f);
    if (idx < numVec4) {
        float4 v = in[idx];
        acc.x += v.x;
        acc.y += v.y;
        acc.z += v.z;
        acc.w += v.w;
    }
    if (idx == 0) outSink[0] = acc;
}

// ----------------------------------------------------------------------------
// 4. VRAM GLOBAL MEMORY WRITE BANDWIDTH KERNEL
// ----------------------------------------------------------------------------
__global__ void vram_write_kernel(float4* __restrict__ out,
                                 float4 val,
                                 int numVec4) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < numVec4) {
        out[idx] = val;
    }
}

// ----------------------------------------------------------------------------
// 5. GAMING SHADER COMPUTE SIMULATION (HIGH ARITHMETIC INTENSITY)
// ----------------------------------------------------------------------------
__global__ void shader_compute_simulation(float* __restrict__ out, int elements) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < elements) {
        float x = (float)idx * 0.001f;
        float a = 1.01f, b = 0.99f;
        #pragma unroll 16
        for (int i = 0; i < 32; ++i) {
            a = a * b + sinf(x);
            b = b * a - cosf(x);
            x += 0.0001f;
        }
        out[idx] = a + b;
    }
}

// ----------------------------------------------------------------------------
// EXPORTED C++ FUNCTIONS
// ----------------------------------------------------------------------------

bool CudaCheckAvailability() {
    int deviceCount = 0;
    cudaError_t err = cudaGetDeviceCount(&deviceCount);
    return (err == cudaSuccess && deviceCount > 0);
}

CudaAiBenchmarkResult RunCudaBenchmarks(int matrixDim, int durationSeconds, double cpuSoloGflops) {
    CudaAiBenchmarkResult res;
    res.cpuIsolatedGflops = cpuSoloGflops;

    int deviceCount = 0;
    if (cudaGetDeviceCount(&deviceCount) != cudaSuccess || deviceCount == 0) {
        res.cudaAvailable = false;
        return res;
    }

    res.cudaAvailable = true;
    cudaDeviceProp prop;
    CUDA_CHECK(cudaGetDeviceProperties(&prop, 0));

    res.deviceName = prop.name;
    res.smCount = prop.multiProcessorCount;
    res.cudaCores = (prop.major == 7 && prop.minor == 5) ? (prop.multiProcessorCount * 64) : (prop.multiProcessorCount * 128);
    res.vramTotalMB = prop.totalGlobalMem / (1024 * 1024);

    size_t freeBytes = 0, totalBytes = 0;
    CUDA_CHECK(cudaMemGetInfo(&freeBytes, &totalBytes));
    res.vramFreeMB = freeBytes / (1024 * 1024);

    // Calculate theoretical VRAM bandwidth via cudaDeviceGetAttribute (compatible with all CUDA versions)
    int memClockKhz = 0, busWidthBits = 0;
    cudaDeviceGetAttribute(&memClockKhz, cudaDevAttrMemoryClockRate, 0);
    cudaDeviceGetAttribute(&busWidthBits, cudaDevAttrGlobalMemoryBusWidth, 0);
    if (memClockKhz > 0 && busWidthBits > 0) {
        res.theoreticalVramBandwidthGBs = (static_cast<double>(memClockKhz) * 1000.0 * 2.0 * (busWidthBits / 8.0)) / 1e9;
    }

    std::cout << "\n=======================================================================\n";
    std::cout << "        PHASE 6-9: CUDA GPU COMPUTE, AI & GAMING BENCHMARKS            \n";
    std::cout << "=======================================================================\n";
    std::cout << "  Device: " << res.deviceName << " (" << res.smCount << " SMs, " << res.cudaCores << " Cores)\n";
    std::cout << "  VRAM:   " << res.vramTotalMB << " MB Total | " << res.vramFreeMB << " MB Free\n";
    std::cout << "-----------------------------------------------------------------------\n";

    // ------------------------------------------------------------------------
    // A. AI DENSE MATRIX MULTIPLICATION (SGEMM)
    // ------------------------------------------------------------------------
    int N = matrixDim;
    if (N <= 0) N = 2048; // Default 2048x2048
    size_t matBytes = N * N * sizeof(float);

    std::cout << "  [1/5] Running AI Dense Matrix Multiply (SGEMM " << N << "x" << N << ")..." << std::flush;

    float *dA = nullptr, *dB = nullptr, *dC = nullptr;
    CUDA_CHECK(cudaMalloc(&dA, matBytes));
    CUDA_CHECK(cudaMalloc(&dB, matBytes));
    CUDA_CHECK(cudaMalloc(&dC, matBytes));

    CUDA_CHECK(cudaMemset(dA, 1, matBytes));
    CUDA_CHECK(cudaMemset(dB, 2, matBytes));

    dim3 block(TILE_SIZE, TILE_SIZE);
    dim3 grid((N + TILE_SIZE - 1) / TILE_SIZE, (N + TILE_SIZE - 1) / TILE_SIZE);

    // Warmup
    sgemm_tiled_kernel<<<grid, block>>>(dA, dB, dC, N);
    CUDA_CHECK(cudaDeviceSynchronize());

    cudaEvent_t startEv, stopEv;
    CUDA_CHECK(cudaEventCreate(&startEv));
    CUDA_CHECK(cudaEventCreate(&stopEv));

    const int sgemmReps = 10;
    CUDA_CHECK(cudaEventRecord(startEv));
    for (int i = 0; i < sgemmReps; ++i) {
        sgemm_tiled_kernel<<<grid, block>>>(dA, dB, dC, N);
    }
    CUDA_CHECK(cudaEventRecord(stopEv));
    CUDA_CHECK(cudaEventSynchronize(stopEv));

    float msTotal = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&msTotal, startEv, stopEv));
    res.sgemmExecutionTimeMs = msTotal / sgemmReps;

    // FLOPs in NxN matrix multiply = 2 * N^3
    double totalFlops = 2.0 * std::pow(static_cast<double>(N), 3);
    res.sgemmComputeTflops = (totalFlops / (res.sgemmExecutionTimeMs / 1000.0)) / 1e12;

    std::cout << " " << std::fixed << std::setprecision(2) << res.sgemmComputeTflops << " TFLOPs ("
              << std::setprecision(2) << res.sgemmExecutionTimeMs << " ms)\n";

    // ------------------------------------------------------------------------
    // B. AI ACTIVATION (GELU) & MEMORY PIPELINE
    // ------------------------------------------------------------------------
    std::cout << "  [2/5] Running Deep Learning Activation Layer (GELU 16M Elems)..." << std::flush;
    const int numVec4 = 4 * 1024 * 1024; // 16M floats = 64 MB
    size_t geluBytes = numVec4 * sizeof(float4);
    float4 *dInGelu = nullptr, *dOutGelu = nullptr;
    CUDA_CHECK(cudaMalloc(&dInGelu, geluBytes));
    CUDA_CHECK(cudaMalloc(&dOutGelu, geluBytes));

    int blockSize = 256;
    int numBlocks = (numVec4 + blockSize - 1) / blockSize;

    CUDA_CHECK(cudaEventRecord(startEv));
    const int geluReps = 20;
    for (int i = 0; i < geluReps; ++i) {
        gelu_activation_kernel<<<numBlocks, blockSize>>>(dInGelu, dOutGelu, numVec4);
    }
    CUDA_CHECK(cudaEventRecord(stopEv));
    CUDA_CHECK(cudaEventSynchronize(stopEv));

    float msGelu = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&msGelu, startEv, stopEv));
    double avgMsGelu = msGelu / geluReps;
    double geluTotalFlops = static_cast<double>(numVec4) * 4.0 * 10.0; // ~10 ops per element
    res.geluThroughputGflops = (geluTotalFlops / (avgMsGelu / 1000.0)) / 1e9;
    res.geluMemoryBandwidthGBs = ((geluBytes * 2.0) / (avgMsGelu / 1000.0)) / 1e9;

    std::cout << " " << std::fixed << std::setprecision(1) << res.geluThroughputGflops << " GFLOPs ("
              << std::setprecision(1) << res.geluMemoryBandwidthGBs << " GB/s)\n";

    // ------------------------------------------------------------------------
    // C. VRAM READ & WRITE BANDWIDTH
    // ------------------------------------------------------------------------
    std::cout << "  [3/5] Measuring VRAM Global Memory Read & Write Bandwidth..." << std::flush;
    float4* dSink = nullptr;
    CUDA_CHECK(cudaMalloc(&dSink, sizeof(float4)));

    // Read Bandwidth
    CUDA_CHECK(cudaEventRecord(startEv));
    for (int i = 0; i < 20; ++i) {
        vram_read_kernel<<<numBlocks, blockSize>>>(dInGelu, dSink, numVec4);
    }
    CUDA_CHECK(cudaEventRecord(stopEv));
    CUDA_CHECK(cudaEventSynchronize(stopEv));
    float msRead = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&msRead, startEv, stopEv));
    res.vramReadBandwidthGBs = (geluBytes * 20.0 / (msRead / 1000.0)) / 1e9;

    // Write Bandwidth
    float4 testVal = make_float4(1.0f, 2.0f, 3.0f, 4.0f);
    CUDA_CHECK(cudaEventRecord(startEv));
    for (int i = 0; i < 20; ++i) {
        vram_write_kernel<<<numBlocks, blockSize>>>(dOutGelu, testVal, numVec4);
    }
    CUDA_CHECK(cudaEventRecord(stopEv));
    CUDA_CHECK(cudaEventSynchronize(stopEv));
    float msWrite = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&msWrite, startEv, stopEv));
    res.vramWriteBandwidthGBs = (geluBytes * 20.0 / (msWrite / 1000.0)) / 1e9;

    std::cout << " Read: " << std::fixed << std::setprecision(1) << res.vramReadBandwidthGBs << " GB/s | "
              << "Write: " << res.vramWriteBandwidthGBs << " GB/s\n";

    // ------------------------------------------------------------------------
    // D. GAMING SHADER PERFORMANCE
    // ------------------------------------------------------------------------
    std::cout << "  [4/5] Measuring Gaming Shader Arithmetic Pipeline..." << std::flush;
    const int shaderElems = 4 * 1024 * 1024;
    float* dShaderOut = nullptr;
    CUDA_CHECK(cudaMalloc(&dShaderOut, shaderElems * sizeof(float)));

    CUDA_CHECK(cudaEventRecord(startEv));
    for (int i = 0; i < 20; ++i) {
        shader_compute_simulation<<<(shaderElems + 255) / 256, 256>>>(dShaderOut, shaderElems);
    }
    CUDA_CHECK(cudaEventRecord(stopEv));
    CUDA_CHECK(cudaEventSynchronize(stopEv));
    float msShader = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&msShader, startEv, stopEv));
    double shaderFlops = static_cast<double>(shaderElems) * 32.0 * 4.0 * 20.0;
    res.shaderComputeTflops = (shaderFlops / (msShader / 1000.0)) / 1e12;
    res.gpuIsolatedTflops = res.sgemmComputeTflops;

    std::cout << " " << std::fixed << std::setprecision(2) << res.shaderComputeTflops << " TFLOPs\n";

    // ------------------------------------------------------------------------
    // E. SIMULTANEOUS CPU + GPU CROSS-THROTTLING TEST (SHARED LAPTOP BUDGET)
    // ------------------------------------------------------------------------
    int simDuration = std::max(5, durationSeconds);
    std::cout << "  [5/5] Testing Simultaneous CPU + GPU Load (" << simDuration << "s Shared Budget Stress)..." << std::flush;

    std::atomic<bool> simRunning{true};
    std::atomic<uint64_t> cpuOps{0};
    std::atomic<uint64_t> gpuGemsDone{0};

    auto simStart = std::chrono::high_resolution_clock::now();

    #pragma omp parallel sections
    {
        // CPU SECTION: All available host threads
        #pragma omp section
        {
            #pragma omp parallel
            {
                double a = 1.0001, b = 0.9999, c = 0.5001;
                while (simRunning.load()) {
                    #pragma unroll 16
                    for (int k = 0; k < 10000; ++k) {
                        a = a * b + c;
                        b = b * a - c;
                    }
                    cpuOps.fetch_add(10000 * 4);
                }
            }
        }

        // GPU SECTION: Continuous SGEMM dispatch
        #pragma omp section
        {
            while (simRunning.load()) {
                sgemm_tiled_kernel<<<grid, block>>>(dA, dB, dC, N);
                cudaDeviceSynchronize();
                gpuGemsDone.fetch_add(1);

                auto now = std::chrono::high_resolution_clock::now();
                if (std::chrono::duration<double>(now - simStart).count() >= simDuration) {
                    simRunning.store(false);
                }
            }
        }
    }

    auto simEnd = std::chrono::high_resolution_clock::now();
    double actualSimSec = std::chrono::duration<double>(simEnd - simStart).count();

    res.cpuCombinedGflops = (static_cast<double>(cpuOps.load()) / actualSimSec) / 1e9;
    double gpuCombinedFlops = static_cast<double>(gpuGemsDone.load()) * totalFlops;
    res.gpuCombinedTflops = (gpuCombinedFlops / actualSimSec) / 1e12;

    if (res.cpuIsolatedGflops > 0.0) {
        res.cpuCrossThrottlePercent = ((res.cpuIsolatedGflops - res.cpuCombinedGflops) / res.cpuIsolatedGflops) * 100.0;
        if (res.cpuCrossThrottlePercent < 0.0) res.cpuCrossThrottlePercent = 0.0;
    }
    if (res.gpuIsolatedTflops > 0.0) {
        res.gpuCrossThrottlePercent = ((res.gpuIsolatedTflops - res.gpuCombinedTflops) / res.gpuIsolatedTflops) * 100.0;
        if (res.gpuCrossThrottlePercent < 0.0) res.gpuCrossThrottlePercent = 0.0;
    }

    std::cout << " Done!\n"
              << "        * GPU Compute: " << std::fixed << std::setprecision(2) << res.gpuCombinedTflops 
              << " TFLOPs (Cross-Throttle: " << std::setprecision(1) << res.gpuCrossThrottlePercent << "%)\n"
              << "        * CPU Compute: " << std::setprecision(1) << res.cpuCombinedGflops 
              << " GFLOPs (Cross-Throttle: " << res.cpuCrossThrottlePercent << "%)\n";

    // Clean up
    cudaFree(dA); cudaFree(dB); cudaFree(dC);
    cudaFree(dInGelu); cudaFree(dOutGelu); cudaFree(dSink);
    cudaFree(dShaderOut);
    cudaEventDestroy(startEv); cudaEventDestroy(stopEv);

    // ------------------------------------------------------------------------
    // AI MODEL SIZE CEILING & GAMING VERDICTS
    // ------------------------------------------------------------------------
    if (res.vramTotalMB >= 16000) {
        res.maxInferenceModelSupported = "Llama-3-70B (Q4 Quantized) / Mistral-Large";
        res.maxFineTuningSupported = "LoRA on 7B & 13B Models Locally";
        res.aiSuitabilityVerdict = "EXCELLENT FOR WORKSTATION AI TRAINING & INFERENCE";
    } else if (res.vramTotalMB >= 8000) {
        res.maxInferenceModelSupported = "Llama-3-8B / Mistral-7B (Q8 / Q4_K_M) / Stable Diffusion XL";
        res.maxFineTuningSupported = "LoRA Fine-Tuning on <= 3B Parameter Models";
        res.aiSuitabilityVerdict = "CAPABLE FOR LOCAL LLM INFERENCE & SMALL LORA TRAINING";
    } else if (res.vramTotalMB >= 6000) {
        res.maxInferenceModelSupported = "Llama-3-8B (Q4_K_S) / Phi-3-mini / Stable Diffusion 1.5";
        res.maxFineTuningSupported = "LoRA on <= 1B Models / Quantized Adapters";
        res.aiSuitabilityVerdict = "MODERATE FOR LIGHT INFERENCE (7B Q4) & SD 1.5";
    } else if (res.vramTotalMB >= 4000) {
        res.maxInferenceModelSupported = "Phi-3-Mini (3.8B Q4) / Gemma-2B / TinyLlama-1.1B";
        res.maxFineTuningSupported = "Fine-Tuning NOT Recommended (VRAM constrained)";
        res.aiSuitabilityVerdict = "ENTRY-LEVEL: Small Quantized Models (<3.8B) / Computer Vision";
    } else {
        res.maxInferenceModelSupported = "TinyLlama-1.1B / NanoGPT / Classical ML (XGBoost/LightGBM)";
        res.maxFineTuningSupported = "NOT SUPPORTED (Insufficient VRAM)";
        res.aiSuitabilityVerdict = "UNSUITABLE FOR MODERN LLM TRAINING";
    }

    if (res.sgemmComputeTflops >= 15.0) {
        res.gamingTierVerdict = "1440p / 4K Ultra Gaming (RTX 4070+ Tier)";
    } else if (res.sgemmComputeTflops >= 8.0) {
        res.gamingTierVerdict = "1080p Ultra / 1440p High Gaming (RTX 3060/4060 Tier)";
    } else if (res.sgemmComputeTflops >= 4.0) {
        res.gamingTierVerdict = "1080p Medium-to-High Gaming (RTX 3050 Tier)";
    } else if (res.sgemmComputeTflops >= 2.0) {
        res.gamingTierVerdict = "1080p Esports / 1080p Medium Gaming (GTX 1650 Tier)";
    } else {
        res.gamingTierVerdict = "720p / 1080p Low Esports Only";
    }

    if (res.gpuCrossThrottlePercent > 15.0 || res.cpuCrossThrottlePercent > 20.0) {
        res.sharedPowerBudgetVerdict = "HEAVY LAPTOP CROSS-THROTTLING: CPU and GPU contend for shared thermal/power budget under simultaneous load.";
    } else {
        res.sharedPowerBudgetVerdict = "BALANCED COOLING & POWER: Laptop maintains dual-component throughput with minimal cross-throttling.";
    }

    return res;
}
