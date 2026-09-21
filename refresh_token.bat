@echo off
title GPT-TYPE Blogger Token Refresher
color 0b
echo ================================================================
echo   GPT-TYPE Blogger 1-Click Authentication
echo ================================================================
echo.
cd /d "%~dp0"
python setup_blogger_auth.py
echo.
pause
