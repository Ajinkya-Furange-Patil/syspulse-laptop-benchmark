@echo off
setlocal
cd /d "%~dp0"

echo =======================================================================
echo   SYSPULSE: PACKAGE CLEAN STANDALONE RUNNER
echo =======================================================================

:: 1. Ensure master binary is built
if not exist "bin\laptop_benchmark.exe" (
    echo [INFO] Binary not found. Building project first...
    call build.bat
)

if not exist "bin\laptop_benchmark.exe" (
    echo [ERROR] Build failed. Could not locate bin\laptop_benchmark.exe.
    pause
    exit /b 1
)

:: 2. Ensure vcomp140.dll is present in bin/
if not exist "bin\vcomp140.dll" (
    if exist "C:\Windows\System32\vcomp140.dll" (
        copy /y "C:\Windows\System32\vcomp140.dll" "bin\vcomp140.dll" >nul
        echo [OK] Bundled OpenMP runtime vcomp140.dll into bin directory
    )
)

:: 3. Create clean SysPulse_Portable directory
set "PORTABLE_DIR=SysPulse_Portable"
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\results"

echo [1/3] Copying standalone SysPulse.exe and runtime DLL...
copy /y "bin\laptop_benchmark.exe" "%PORTABLE_DIR%\SysPulse.exe" >nul
if exist "bin\vcomp140.dll" copy /y "bin\vcomp140.dll" "%PORTABLE_DIR%\" >nul

echo [2/3] Signing portable SysPulse.exe with Ajinkya Furange digital signature...
if exist "scripts\sign_binary.ps1" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\sign_binary.ps1" "%PORTABLE_DIR%\SysPulse.exe"
)

echo [3/3] Creating standalone ZIP archive...
powershell -Command "if (Test-Path 'SysPulse_Portable.zip') { Remove-Item 'SysPulse_Portable.zip' -Force }; Compress-Archive -Path 'SysPulse_Portable\*' -DestinationPath 'SysPulse_Portable.zip'"

echo.
echo =======================================================================
echo   CLEAN PORTABLE PACKAGE READY!
echo =======================================================================
echo   Folder:  SysPulse_Portable\
echo   Archive: SysPulse_Portable.zip
echo.
echo Standalone folder contains ONLY:
echo   - SysPulse.exe  (Double-click to run - opens report in browser automatically)
echo   - vcomp140.dll  (Bundled runtime)
echo   - results\      (Output directory)
echo =======================================================================
pause
