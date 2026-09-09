@echo off
:: Backward-compatibility wrapper delegating to root build.bat
call "%~dp0build.bat" %*
