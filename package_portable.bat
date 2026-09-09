@echo off
setlocal
cd /d "%~dp0"

echo =======================================================================
echo   SYSPULSE: PACKAGE STANDALONE PORTABLE RUNNER FOR USB AND RETAIL SHOPS
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

:: 3. Create SysPulse_Portable directory
set "PORTABLE_DIR=SysPulse_Portable"
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\results"

echo [1/3] Copying executable and runtime DLLs...
copy /y "bin\laptop_benchmark.exe" "%PORTABLE_DIR%\" >nul
if exist "bin\vcomp140.dll" copy /y "bin\vcomp140.dll" "%PORTABLE_DIR%\" >nul

echo [2/3] Generating portable runner script...
echo @echo off > "%PORTABLE_DIR%\run_portable.bat"
echo setlocal >> "%PORTABLE_DIR%\run_portable.bat"
echo cd /d "%%~dp0" >> "%PORTABLE_DIR%\run_portable.bat"
echo echo ======================================================================= >> "%PORTABLE_DIR%\run_portable.bat"
echo echo   SYSPULSE PORTABLE: 34-POINT LAPTOP BUYER INSPECTION RUNNER >> "%PORTABLE_DIR%\run_portable.bat"
echo echo ======================================================================= >> "%PORTABLE_DIR%\run_portable.bat"
echo echo Running standalone hardware audit and stress test... >> "%PORTABLE_DIR%\run_portable.bat"
echo echo No installation, no internet, and no admin rights required! >> "%PORTABLE_DIR%\run_portable.bat"
echo echo. >> "%PORTABLE_DIR%\run_portable.bat"
echo if not exist "results" mkdir results >> "%PORTABLE_DIR%\run_portable.bat"
echo laptop_benchmark.exe %%* >> "%PORTABLE_DIR%\run_portable.bat"
echo echo. >> "%PORTABLE_DIR%\run_portable.bat"
echo echo [INFO] Inspection complete! >> "%PORTABLE_DIR%\run_portable.bat"
echo if exist "results\laptop_buyer_inspection.html" start "" "results\laptop_buyer_inspection.html" >> "%PORTABLE_DIR%\run_portable.bat"
echo pause >> "%PORTABLE_DIR%\run_portable.bat"

echo ======================================================================= > "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo   SYSPULSE PORTABLE - QUICK INSTRUCTIONS FOR BUYING A LAPTOP >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo ======================================================================= >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo. >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo 1. Copy this entire SysPulse_Portable folder onto a USB pendrive. >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo 2. Plug the USB drive into the new or demo laptop in the shop. >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo 3. Double-click run_portable.bat. >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo 4. Wait ~30 to 60 seconds while it audits: >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo      * Real CPU physical vs logical cores and AVX-512 support >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo      * Single-channel vs Dual-channel RAM bottleneck >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo      * Real GPU TGP, VRAM capacity, and local AI model fit >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo      * Thermal throttling, cooling efficiency, and sustained power >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo      * NVMe storage read speed >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo 5. Review the 34-point scorecard and dealbreakers that open >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo    automatically in the web browser! >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo. >> "%PORTABLE_DIR%\HOW_TO_USE.txt"
echo NOTE: No internet connection, admin privileges, or setup required. >> "%PORTABLE_DIR%\HOW_TO_USE.txt"

echo [3/3] Creating standalone ZIP archive...
powershell -Command "if (Test-Path 'SysPulse_Portable.zip') { Remove-Item 'SysPulse_Portable.zip' -Force }; Compress-Archive -Path 'SysPulse_Portable\*' -DestinationPath 'SysPulse_Portable.zip'"

echo.
echo =======================================================================
echo   PORTABLE PACKAGE CREATED SUCCESSFULLY!
echo =======================================================================
echo   Folder:  SysPulse_Portable\
echo   Archive: SysPulse_Portable.zip
echo.
echo You can now copy 'SysPulse_Portable.zip' or the folder to any USB drive
echo and run it on ANY new laptop out of the box!
echo =======================================================================
pause
