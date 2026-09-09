@echo off
setlocal
cd /d "%~dp0"

echo =======================================================================
echo   SYSPULSE BENCHMARK SUITE - CLEANUP WORKSPACE
echo =======================================================================

echo Cleaning build artifacts and binaries...

if exist "build" (
    del /q /f build\* 2>nul
    echo   [OK] Cleaned build\
)

if exist "bin" (
    del /q /f bin\* 2>nul
    echo   [OK] Cleaned bin\
)

echo Workspace reset complete.
pause
