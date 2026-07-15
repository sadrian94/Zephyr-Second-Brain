@echo off
title Zephyr File Watcher
cd /d "%~dp0"
echo Starting Zephyr File Watcher...
echo Press Ctrl+C to stop the watcher.
echo =======================================
python System\zephyr-watcher.py
pause
