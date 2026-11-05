@echo off
title CRT Webhook Server (TradingView to Telegram)
cd /d "%~dp0"
echo ======================================================
echo   Menjalankan Server Webhook CRT Telegram
echo ======================================================
python webhook_server.py
pause
