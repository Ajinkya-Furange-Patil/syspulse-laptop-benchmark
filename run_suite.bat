@echo off
:: Backward-compatibility wrapper delegating to root run.bat
call "%~dp0run.bat" %*
