@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0..\.."

echo =======================================================================
echo   PC BENCHMARK SUITE - PHASE 0 AUDIT BUILD AND RUNNER
echo =======================================================================

:: 1. Check if cl.exe is already available in PATH
where cl.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MSVC C++ compiler detected in current environment.
    goto COMPILE
)

echo [INFO] Searching for Visual Studio environment...

:: 2. Use vswhere.exe if present
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" (
    for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -property installationPath`) do (
        set "VS_INSTALL=%%i"
        if exist "%%i\VC\Auxiliary\Build\vcvars64.bat" (
            set "VS_PATH=%%i\VC\Auxiliary\Build\vcvars64.bat"
            goto FOUND_VS
        )
    )
)

:: 3. Check explicit standard locations
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
    echo [OK] Initializing 64-bit developer environment via:
    echo      !VS_PATH!
    call "!VS_PATH!"
    goto COMPILE
)

echo [ERROR] Visual Studio 2022 C++ build environment could not be located.
echo         Please ensure "Desktop development with C++" is installed.
pause
exit /b 1

:COMPILE
echo.
echo [1/3] Creating output directories...
if not exist "bin" mkdir bin
if not exist "results" mkdir results
if not exist "build" mkdir build

echo.
echo [2/3] Compiling src\phases\phase0_audit\main_audit.cpp...
cl /nologo /O2 /std:c++20 /EHsc /W4 /D_CRT_SECURE_NO_WARNINGS src\phases\phase0_audit\main_audit.cpp /Fe:bin\sys_audit.exe /Fo:build\ wbemuuid.lib ole32.lib oleaut32.lib Advapi32.lib

if %errorlevel% neq 0 (
    echo [ERROR] Compilation failed! Check the error messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo =======================================================================
echo   [3/3] EXECUTING PHASE 0 HARDWARE AUDIT
echo =======================================================================
bin\sys_audit.exe

echo.
echo Telemetry exported to results\system_info.json.
pause
