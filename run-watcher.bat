@echo off
title Zephyr File Watcher
cd /d "%~dp0"
echo Starting Zephyr v0.3 Safe Refresh Watcher...
echo Press Ctrl+C to stop the watcher.
echo =======================================
python System\zephyr-watcher.py
pause
