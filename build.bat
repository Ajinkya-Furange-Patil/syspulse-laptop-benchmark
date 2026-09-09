@echo off
setlocal enabledelayedexpansion

echo =======================================================================
echo   SYSPULSE: PC BENCHMARK AND LAPTOP EVALUATION SUITE - BUILDER
echo =======================================================================

:: 1. Check if cl.exe is already active in current environment
where cl.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MSVC C++ compiler detected in current environment.
    goto SETUP_CUDA
)

:: 2. Locate Visual Studio 2022 / 2019 64-bit developer environment
echo [INFO] Searching for Visual Studio C++ build environment...
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" (
    for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -property installationPath`) do (
        if exist "%%i\VC\Auxiliary\Build\vcvars64.bat" (
            set "VS_PATH=%%i\VC\Auxiliary\Build\vcvars64.bat"
            goto FOUND_VS
        )
    )
)

if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    set "VS_PATH=%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
    goto FOUND_VS
)
if exist "%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    set "VS_PATH=%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
    goto FOUND_VS
)
if exist "%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    set "VS_PATH=%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
    goto FOUND_VS
)
if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    set "VS_PATH=%ProgramFiles(x86)%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
    goto FOUND_VS
)

:FOUND_VS
if defined VS_PATH (
    echo [OK] Initializing MSVC Developer Environment via:
    echo      !VS_PATH!
    call "!VS_PATH!"
    goto SETUP_CUDA
)

echo [ERROR] Visual Studio C++ environment could not be found.
echo         Please install Visual Studio with "Desktop development with C++".
pause
exit /b 1

:SETUP_CUDA
:: 3. Check for CUDA Toolkit
if defined CUDA_PATH goto CONFIGURE_CUDA
if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3" (
    set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3"
    goto CONFIGURE_CUDA
)
if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6" (
    set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6"
    goto CONFIGURE_CUDA
)
if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4" (
    set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4"
    goto CONFIGURE_CUDA
)

where nvcc.exe >nul 2>&1
if %errorlevel% equ 0 goto CONFIGURE_CUDA

:: If CUDA is absent, proceed to CPU fallback
goto CUDA_NOT_FOUND

:CONFIGURE_CUDA
set "HAS_CUDA=1"
set "PATH=%CUDA_PATH%\bin;%PATH%"
set "LIB=%CUDA_PATH%\lib\x64;%LIB%"
set "INCLUDE=%CUDA_PATH%\include;%INCLUDE%"
echo [OK] NVIDIA CUDA Toolkit detected at:
echo      %CUDA_PATH%
goto PREPARE_DIRS

:CUDA_NOT_FOUND
set "HAS_CUDA=0"
echo [INFO] CUDA Toolkit not found. Building in Universal CPU/Host mode (AMD/Intel iGPU compatible).

:PREPARE_DIRS
if not exist "bin" mkdir bin
if not exist "build" mkdir build
if not exist "results" mkdir results

:: Compile Windows Version Resource (Embeds 'Ajinkya Furange' metadata)
where rc.exe >nul 2>&1
if %errorlevel% equ 0 (
    rc /nologo /fo build\version.res src\version.rc
) else if exist "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\rc.exe" (
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\rc.exe" /nologo /fo build\version.res src\version.rc
)
set "RES_OBJ="
if exist "build\version.res" set "RES_OBJ=build\version.res"

if "%HAS_CUDA%"=="1" goto BUILD_CUDA
goto BUILD_CPU_FALLBACK

:BUILD_CUDA
echo.
echo [1/2] Compiling CUDA Kernels (src\cuda_kernels.cu)...
nvcc -O3 -c src\cuda_kernels.cu -o build\cuda_kernels.obj -Iinclude -Xcompiler "/openmp /EHsc /D_CRT_SECURE_NO_WARNINGS"
if %errorlevel% neq 0 (
    echo [WARNING] CUDA compilation failed. Falling back to CPU mode...
    goto BUILD_CPU_FALLBACK
)

echo.
echo [2/2] Compiling Master Benchmark Executable with CUDA Support...
cl /nologo /O2 /std:c++20 /openmp /EHsc /W3 /D_CRT_SECURE_NO_WARNINGS /Iinclude /I"%CUDA_PATH%\include" src\main.cpp build\cuda_kernels.obj %RES_OBJ% /Fe:bin\laptop_benchmark.exe /Fo:build\ /link /LIBPATH:"%CUDA_PATH%\lib\x64" cudart.lib Powrprof.lib wbemuuid.lib ole32.lib oleaut32.lib Advapi32.lib Shell32.lib
if %errorlevel% neq 0 (
    echo [ERROR] Linking failed!
    pause
    exit /b %errorlevel%
)
goto SIGN_BINARY

:BUILD_CPU_FALLBACK
echo.
echo [1/2] Compiling CPU/Host Fallback Layer (src\cuda_stub.cpp)...
cl /nologo /O2 /std:c++20 /EHsc /W3 /D_CRT_SECURE_NO_WARNINGS /Iinclude /c src\cuda_stub.cpp /Fo:build\cuda_stub.obj
if %errorlevel% neq 0 (
    echo [ERROR] Compilation of fallback layer failed!
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] Compiling Master Benchmark Executable (Universal CPU Mode)...
cl /nologo /O2 /std:c++20 /openmp /EHsc /W3 /D_CRT_SECURE_NO_WARNINGS /Iinclude src\main.cpp build\cuda_stub.obj %RES_OBJ% /Fe:bin\laptop_benchmark.exe /Fo:build\ Powrprof.lib wbemuuid.lib ole32.lib oleaut32.lib Advapi32.lib Shell32.lib
if %errorlevel% neq 0 (
    echo [ERROR] Linking failed!
    pause
    exit /b %errorlevel%
)

:SIGN_BINARY
if exist "scripts\sign_binary.ps1" (
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\sign_binary.ps1" "bin\laptop_benchmark.exe"
)

:BUILD_SUCCESS
echo.
echo =======================================================================

echo   BUILD COMPLETED SUCCESSFULLY!
echo   Executable generated: bin\laptop_benchmark.exe
echo =======================================================================
echo You can run the benchmark by double-clicking 'run.bat' or bin\laptop_benchmark.exe.
pause
