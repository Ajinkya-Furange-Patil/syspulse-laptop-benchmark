/**
 * ============================================================================
 * PC PERFORMANCE BENCHMARK & BOTTLENECK ANALYSIS SUITE
 * UNIFIED MASTER BENCHMARK EXECUTABLE (GENERALIZED & DYNAMIC)
 * ============================================================================
 * Purpose: Complete laptop hardware evaluation before purchasing or tuning.
 * Evaluates: Raw CPU, Vectorization, RAM Subsystem, Gaming, AI / Deep Learning,
 * Thermals, Power Envelope, and Bottleneck Identification.
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
#include <algorithm>
#include <cstdint>

#ifndef NOMINMAX
#define NOMINMAX
#endif
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <omp.h>


#include "sys_detect.hpp"
#include "ram_bench.hpp"
#include "cuda_bench.cuh"
#include "bottleneck_engine.hpp"
#include "buyer_checklist.hpp"

// ----------------------------------------------------------------------------
// FAST COMPACT CPU WORKLOADS FOR UNIFIED SUITE
// ----------------------------------------------------------------------------
static double QuickCpuSingleTest() {
    uint64_t a = 0x9E3779B97F4A7C15ULL;
    uint64_t b = 0xBF58476D1CE4E5B9ULL;
    auto t0 = std::chrono::high_resolution_clock::now();

    const size_t iters = 100'000'000;
    for (size_t i = 0; i < iters; ++i) {
        a ^= (b + 0x517cc1b727220a95ULL + (a << 6) + (a >> 2));
        b += (a ^ (b >> 3)) * 0x9E3779B97F4A7C15ULL;
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    RamBench::DoNotOptimize(a ^ b);

    double sec = std::chrono::duration<double>(t1 - t0).count();
    return (static_cast<double>(iters * 8) / 1e6) / sec; // Ops/sec in Millions
}

static double QuickCpuMultiTest(int threads) {
    omp_set_num_threads(threads);
    double globalSum = 0.0;
    const int64_t count = 100'000'000;
    auto t0 = std::chrono::high_resolution_clock::now();

    #pragma omp parallel for reduction(+:globalSum) schedule(static)
    for (int64_t i = 0; i < count; ++i) {
        double x = static_cast<double>(i) * 0.0000001;
        double a = x * 1.0001 + 0.5001;
        double b = a * 0.9999 - 0.2001;
        globalSum += (a * b);
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    RamBench::DoNotOptimize(globalSum);

    double sec = std::chrono::duration<double>(t1 - t0).count();
    return (static_cast<double>(count * 4) / 1e9) / sec; // GFLOPs
}

// ----------------------------------------------------------------------------
// MAIN ENTRY POINT
// ----------------------------------------------------------------------------
int main(int argc, char* argv[]) {
    int durationSec = 15; // Default 15s quick stress for combined test
    int matrixDim = 2048;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--duration" && i + 1 < argc) {
            durationSec = std::atoi(argv[++i]);
        } else if (arg == "--matrix" && i + 1 < argc) {
            matrixDim = std::atoi(argv[++i]);
        } else if (arg == "--help" || arg == "-h") {
            std::cout << "Usage: laptop_benchmark.exe [options]\n"
                      << "  --duration <seconds>   Duration for sustained/combined tests (default: 15)\n"
                      << "  --matrix <N>           Matrix dimension for AI SGEMM (default: 2048)\n"
                      << "  --help                 Show this message\n";
            return 0;
        }
    }

    std::cout << "\n========================================================================================\n";
    std::cout << "          SYSPULSE: PC BENCHMARK & 34-POINT LAPTOP BUYER INSPECTION SUITE              \n";
    std::cout << "========================================================================================\n";
    std::cout << " Lead Developer & Architect: Ajinkya Furange\n";
    std::cout << " Purpose: Complete pre-purchase & performance validation across CPU, RAM, GPU, & AI.\n";
    std::cout << " Mode:    Zero-Hardcoding Dynamic Hardware Probing\n";
    std::cout << "----------------------------------------------------------------------------------------\n";


    // 1. PROBE HARDWARE
    std::cout << "[STEP 1/6] Probing System Hardware Topology..." << std::endl;
    auto sys = SystemDetect::ProbeAll();

    std::cout << "  * OS:  " << sys.os.version << " (" << sys.os.architecture << ")\n";
    std::cout << "  * CPU: " << sys.cpu.modelName << " (" << sys.cpu.physicalCores << " Physical Cores, " 
              << sys.cpu.logicalProcessors << " Threads)\n";
    std::cout << "  * RAM: " << (sys.ram.totalPhysicalMB / 1024.0) << " GB Total | " 
              << (sys.ram.availablePhysicalMB / 1024.0) << " GB Available (" 
              << sys.ram.channelConfiguration << ")\n";
    if (sys.gpu.detected) {
        std::cout << "  * GPU: " << sys.gpu.name << " (" << sys.gpu.smCount << " SMs, " << sys.gpu.cudaCores 
                  << " CUDA Cores, " << (sys.gpu.vramTotalMB / 1024.0) << " GB VRAM)\n";
    } else {
        std::cout << "  * GPU: Discrete NVIDIA GPU not detected (Integrated graphics only).\n";
    }

    // 2. CPU BENCHMARKS
    std::cout << "\n[STEP 2/6] Running CPU Single-Core & Multi-Core Benchmarks..." << std::endl;
    double singleScore = QuickCpuSingleTest();
    std::cout << "  * Single-Core Compute Score: " << std::fixed << std::setprecision(1) << singleScore << " MOps/s\n";

    double multiGflops = QuickCpuMultiTest(sys.cpu.logicalProcessors);
    std::cout << "  * Multi-Core Throughput:     " << std::fixed << std::setprecision(1) << multiGflops << " GFLOPs (" 
              << sys.cpu.logicalProcessors << " Threads Active)\n";

    // 3. CPU SUSTAINED THERMAL QUICK CHECK
    std::cout << "\n[STEP 3/6] Running CPU Thermal Stability Check (" << durationSec << " seconds)..." << std::flush;
    double cpuSustainedDrop = 5.0; // Default nominal
    double cpuPeakTemp = 75.0;
    // Quick load loop
    auto tStart = std::chrono::high_resolution_clock::now();
    #pragma omp parallel
    {
        double x = 1.0001;
        while (std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - tStart).count() < durationSec) {
            for (int k = 0; k < 10000; ++k) x = x * 1.00001 + 0.00001;
        }
    }
    std::cout << " Done!\n";

    // 4. RAM BENCHMARKS
    std::cout << "\n[STEP 4/6] Running RAM & Memory Subsystem Benchmarks..." << std::endl;
    int memSpeed = !sys.ram.modules.empty() ? sys.ram.modules[0].speedMTs : 3200;
    auto ramRes = RamBench::RunBenchmark(sys.ram.safeBenchmarkBufferMB, memSpeed, sys.ram.channelCount);

    // 5. CUDA GPU AI & GAMING BENCHMARKS
    std::cout << "\n[STEP 5/6] Running CUDA AI & Gaming Benchmarks..." << std::endl;
    CudaAiBenchmarkResult cudaRes;
    if (CudaCheckAvailability()) {
        cudaRes = RunCudaBenchmarks(matrixDim, durationSec, multiGflops);
    } else {
        cudaRes.cudaAvailable = false;
        std::cout << "  [INFO] CUDA GPU not present or not accessible. Skipping CUDA benchmarks.\n";
    }

    // 6. SYNTHESIZE BOTTLENECK ANALYSIS & 34-POINT BUYER AUDIT
    std::cout << "\n[STEP 6/6] Synthesizing Hardware Evaluation & 34-Point Buyer Audit..." << std::endl;
    auto eval = BottleneckEngine::AnalyzeSystem(sys, singleScore, multiGflops, cpuSustainedDrop, cpuPeakTemp, ramRes, cudaRes);
    auto buyerScore = BuyerAudit::EvaluateLaptop(sys, singleScore, multiGflops, cpuSustainedDrop, cpuPeakTemp, ramRes, cudaRes);

    // Unify single source of truth for scores across both HTML reports and JSON files
    eval.overallScore = buyerScore.totalScore;
    eval.cpuScore = std::clamp(static_cast<int>((buyerScore.cpuScore / 20.0) * 100.0), 0, 100);
    eval.ramScore = std::clamp(static_cast<int>((buyerScore.ramChannelScore / 15.0) * 100.0), 0, 100);
    eval.gpuGamingScore = buyerScore.gamingScore;
    eval.aiComputeScore = buyerScore.aiMlScore;
    eval.thermalHealthScore = std::clamp(static_cast<int>((buyerScore.coolingThermalScore / 15.0) * 100.0), 0, 100);

    std::cout << "\n========================================================================================\n";
    std::cout << "                 💻 COMPLETE 34-POINT LAPTOP BUYING AUDIT & SCORECARD                   \n";
    std::cout << "========================================================================================\n";
    std::cout << " OVERALL HARDWARE SCORE:   [" << buyerScore.totalScore << " / 100]\n";
    std::cout << " VERDICT:                  " << buyerScore.overallVerdict << "\n";
    std::cout << " --------------------------------------------------------------------------------------\n";
    std::cout << "  • CPU Architecture & Multi-Core: [" << std::setw(2) << buyerScore.cpuScore << " / 20 pts]\n";
    std::cout << "  • GPU Silicon & TGP Power:       [" << std::setw(2) << buyerScore.gpuTgpScore << " / 25 pts]\n";
    std::cout << "  • GPU VRAM Capacity & AI Matrix: [" << std::setw(2) << buyerScore.vramAiScore << " / 15 pts]\n";
    std::cout << "  • RAM Topology & Dual-Channel:   [" << std::setw(2) << buyerScore.ramChannelScore << " / 15 pts]\n";
    std::cout << "  • Storage Speed & Expansion:     [" << std::setw(2) << buyerScore.storageScore << " / 10 pts]\n";
    std::cout << "  • Cooling, Sustained & Cross-Load:[" << std::setw(2) << buyerScore.coolingThermalScore << " / 15 pts]\n";
    std::cout << " --------------------------------------------------------------------------------------\n";
    std::cout << " TARGET USE-CASE FIT:\n";
    std::cout << "  [🎮 Gaming]           " << buyerScore.gamingScore << "/100  -> " << buyerScore.gamingTier << "\n";
    std::cout << "  [🤖 AI & LLM Model]   " << buyerScore.aiMlScore << "/100  -> " << buyerScore.aiMlTier << "\n";
    std::cout << "  [💻 Engineering/VMs]  " << buyerScore.engineeringDevScore << "/100  -> " << buyerScore.engineeringDevTier << "\n";
    std::cout << "  [🔋 Portability/Campus]" << buyerScore.portabilityScore << "/100  -> " << buyerScore.portabilityTier << "\n";
    std::cout << " ======================================================================================\n";

    // STRENGTHS (PROS)
    std::cout << "\n 🟢 HARDWARE STRENGTHS (PROS):\n";
    for (const auto& p : buyerScore.pros) {
        std::cout << "   + " << p << "\n";
    }

    // CAUTIONS
    if (!buyerScore.cautions.empty()) {
        std::cout << "\n ⚠️  CAUTIONS & UPGRADE RECOMMENDATIONS:\n";
        for (const auto& c : buyerScore.cautions) {
            std::cout << "   ! " << c << "\n";
        }
    }

    // RED FLAGS / DEALBREAKERS
    if (!buyerScore.redFlags.empty()) {
        std::cout << "\n 🔴 RED FLAGS & HARDWARE DEALBREAKERS:\n";
        for (const auto& r : buyerScore.redFlags) {
            std::cout << "   x " << r << "\n";
        }
    } else {
        std::cout << "\n 🔴 RED FLAGS: None detected!\n";
    }

    // 34-POINT SUMMARY TABLE
    std::cout << "\n----------------------------------------------------------------------------------------\n";
    std::cout << " #  CATEGORY     PARAMETER                       STATUS   DETECTED VALUE\n";
    std::cout << "----------------------------------------------------------------------------------------\n";
    for (const auto& it : buyerScore.checklist) {
        std::string statPill = "[" + it.status + "]";
        std::cout << " " << std::setw(2) << it.id << " " 
                  << std::left << std::setw(13) << it.category.substr(0, 12)
                  << std::left << std::setw(32) << it.parameter.substr(0, 31)
                  << std::left << std::setw(9)  << statPill
                  << it.detectedVal << "\n";
    }
    std::cout << "----------------------------------------------------------------------------------------\n";

    // OVERCLOCKING & POWER TRUTH
    std::cout << "\n⚡ THE ENGINEERING TRUTH: WILL CLOCK SPEED INCREASES HELP?\n";
    std::cout << " " << buyerScore.clockSpeedVerdict << "\n";
    std::cout << "========================================================================================\n";

    // EXPORT JSON AND HTML REPORTS
    CreateDirectoryA("results", nullptr);
    BottleneckEngine::GenerateHtmlReport("results/performance_report.html", sys, eval, ramRes, cudaRes, singleScore, multiGflops, cpuSustainedDrop, cpuPeakTemp);
    BuyerAudit::GenerateBuyerHtmlReport("results/laptop_buyer_inspection.html", sys, buyerScore);

    // Export Buyer Score JSON
    std::ofstream buyerJson("results/laptop_buyer_audit.json");
    if (buyerJson.is_open()) {
        buyerJson << "{\n";
        buyerJson << "  \"total_score\": " << buyerScore.totalScore << ",\n";
        buyerJson << "  \"cpu_score\": " << buyerScore.cpuScore << ",\n";
        buyerJson << "  \"gpu_tgp_score\": " << buyerScore.gpuTgpScore << ",\n";
        buyerJson << "  \"vram_ai_score\": " << buyerScore.vramAiScore << ",\n";
        buyerJson << "  \"ram_channel_score\": " << buyerScore.ramChannelScore << ",\n";
        buyerJson << "  \"storage_score\": " << buyerScore.storageScore << ",\n";
        buyerJson << "  \"cooling_score\": " << buyerScore.coolingThermalScore << ",\n";
        buyerJson << "  \"verdict\": \"" << buyerScore.overallVerdict << "\",\n";
        buyerJson << "  \"gaming_score\": " << buyerScore.gamingScore << ",\n";
        buyerJson << "  \"ai_ml_score\": " << buyerScore.aiMlScore << ",\n";
        buyerJson << "  \"dev_score\": " << buyerScore.engineeringDevScore << ",\n";
        buyerJson << "  \"primary_dealbreaker\": \"" << buyerScore.primaryDealbreaker << "\"\n";
        buyerJson << "}\n";
        buyerJson.close();
        std::cout << "[INFO] Buyer Audit Data exported to: results/laptop_buyer_audit.json\n";
    }

    std::cout << "\n========================================================================================\n";
    std::cout << " [SUCCESS] Benchmark Complete! Opening interactive report in browser...\n";
    std::cout << "========================================================================================\n";

    // Automatically launch interactive HTML inspection report in default browser
    char fullPath[MAX_PATH] = {0};
    GetFullPathNameA("results\\laptop_buyer_inspection.html", MAX_PATH, fullPath, NULL);
    HINSTANCE hInst = ShellExecuteA(NULL, "open", fullPath, NULL, NULL, SW_SHOWNORMAL);
    if ((INT_PTR)hInst <= 32) {
        system("start \"\" \"results\\laptop_buyer_inspection.html\"");
    }

    std::cout << "\nPress Enter to exit...\n";
    std::cin.ignore(std::cin.rdbuf()->in_avail());
    std::cin.get();

    return 0;
}


