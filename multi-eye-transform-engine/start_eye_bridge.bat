@echo off
title Eye Bridge — localhost:8766
cd /d "%~dp0"
echo.
echo  =========================================
echo   Multi-Eye Transform Engine - Eye Bridge
echo   localhost:8766  (for alive/eye.html)
echo  =========================================
echo.
python eye_bridge.py
pause
