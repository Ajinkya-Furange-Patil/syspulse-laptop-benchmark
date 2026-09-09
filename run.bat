@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo =======================================================================
echo   SYSPULSE: ALL-IN-ONE PC BENCHMARK ^& LAPTOP EVALUATION RUNNER
echo =======================================================================

:: 1. Auto-compile if binary has not been built yet
if not exist "bin\laptop_benchmark.exe" (
    echo [INFO] Benchmark binary not found. Building project automatically...
    call build.bat
)

if not exist "bin\laptop_benchmark.exe" (
    echo [ERROR] Could not find or build bin\laptop_benchmark.exe!
    pause
    exit /b 1
)

:: 2. Ensure CUDA runtime DLLs are accessible if CUDA Toolkit is installed
if defined CUDA_PATH (
    if exist "!CUDA_PATH!\bin" set "PATH=!CUDA_PATH!\bin;!PATH!"
)
if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\bin" (
    set "PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\bin;!PATH!"
) else if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin" (
    set "PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin;!PATH!"
) else if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin" (
    set "PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin;!PATH!"
)

:: 3. Execute Master Benchmark
echo.
bin\laptop_benchmark.exe %*

set "BENCH_EXIT=%errorlevel%"
if %BENCH_EXIT% neq 0 (
    echo.
    echo [WARNING] Benchmark exited with code %BENCH_EXIT%.
    pause
    exit /b %BENCH_EXIT%
)

:: 4. Automatically open the interactive HTML Inspection Report
echo.
echo [INFO] Benchmark completed successfully!
if exist "results\laptop_buyer_inspection.html" (
    echo [INFO] Opening interactive 34-Point Buyer Inspection Report in default browser...
    start "" "results\laptop_buyer_inspection.html"
) else if exist "results\performance_report.html" (
    echo [INFO] Opening interactive Performance Report in default browser...
    start "" "results\performance_report.html"
)

echo.
pause
