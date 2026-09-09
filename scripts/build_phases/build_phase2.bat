@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0..\.."

echo =======================================================================
echo   PC BENCHMARK SUITE - PHASE 2 CPU SINGLE-CORE BUILD AND RUNNER
echo =======================================================================

where cl.exe >nul 2>&1
if %errorlevel% equ 0 (
    goto COMPILE
)

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

:FOUND_VS
if defined VS_PATH (
    echo [OK] Initializing 64-bit developer environment via:
    echo      !VS_PATH!
    call "!VS_PATH!"
    goto COMPILE
)

echo [ERROR] Visual Studio 2022 C++ environment could not be found.
pause
exit /b 1

:COMPILE
if not exist "bin" mkdir bin
if not exist "results" mkdir results
if not exist "build" mkdir build

echo.
echo [1/2] Compiling src\phases\phase2_cpu_single\main_cpu_single.cpp (/arch:AVX512)...
cl /nologo /O2 /std:c++20 /arch:AVX512 /EHsc /W4 /D_CRT_SECURE_NO_WARNINGS src\phases\phase2_cpu_single\main_cpu_single.cpp /Fe:bin\cpu_single.exe /Fo:build\ Powrprof.lib Advapi32.lib

if %errorlevel% neq 0 (
    echo [ERROR] Compilation failed!
    pause
    exit /b %errorlevel%
)

echo.
echo =======================================================================
echo   [2/2] EXECUTING PHASE 2 CPU SINGLE-THREAD BENCHMARK
echo =======================================================================
bin\cpu_single.exe

echo.
pause
