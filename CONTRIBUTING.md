# Contributing to SysPulse

Thank you for your interest in contributing to **SysPulse**! This project aims to empower students, gamers, and developers with transparent hardware evaluation before purchasing or tuning laptops and PCs.

---

## 🛠️ How to Get Started

1. **Fork the Repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/syspulse-laptop-benchmark.git
   cd syspulse-laptop-benchmark
   ```
3. **Build the project**:
   - Double-click `build.bat` or run:
     ```cmd
     build.bat
     ```
4. **Test your build**:
   - Run `run.bat` or:
     ```cmd
     bin\laptop_benchmark.exe --duration 10
     ```

---

## 💡 High-Impact Contribution Ideas

We welcome contributions across all areas of hardware analysis! Here are high-priority areas:

1. **DirectCompute / DirectML GPU Support**:
   - Implement an alternative GPU benchmark using DirectX 12 / DirectML so AMD Radeon and Intel Arc/Iris Xe GPUs can be benchmarked for TFLOPs without NVIDIA CUDA.
2. **Disk I/O Stress Benchmark**:
   - Add a CrystalDiskMark-style test checking sequential and 4K random read/write speeds, detecting SLC cache drop-offs.
3. **Battery Drain & Wattage Efficiency**:
   - Measure power draw in milliwatts/Joules over a standard workload to report real-world battery life estimates.
4. **Peripherals & Display QA**:
   - Add dead-pixel check screens, keyboard ghosting test, and audio latency diagnostic for second-hand laptop buyers.
5. **Interactive GUI / Desktop Frontend**:
   - Add an ImGui, Qt, or Tauri native dashboard showing live clock speed, temperature, and power graphs in real time.

---

## 📝 Submitting a Pull Request

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feat/directml-gpu-bench
   ```
2. Commit your changes with clear messages:
   ```bash
   git commit -m "feat(gpu): add DirectML matrix multiplication for AMD/Intel graphics"
   ```
3. Push to your fork and submit a Pull Request on GitHub.
4. Ensure code adheres to standard C++20 guidelines and does not introduce memory leaks.

---

## 📜 Code Style Guidelines
- Standard: Modern C++20.
- Keep dependencies minimal (prefer Windows SDK headers and native APIs).
- Maintain robust error handling for absent hardware features.
