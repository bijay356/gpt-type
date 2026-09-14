@echo off
title Launching GPT-TYPE Desktop...
cd /d "%~dp0"

echo ========================================================
echo   GPT-TYPE 123+ Languages Offline Desktop Software
echo ========================================================
echo.

set "EDGE_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE_PATH%" (
    set "EDGE_PATH=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

if exist "%EDGE_PATH%" (
    echo Starting GPT-TYPE in standalone application window...
    start "" "%EDGE_PATH%" --app="file:///%~dp0index.html" --window-size=1320,860
    exit /b 0
)

echo Microsoft Edge not found in standard paths, launching in default browser...
start "" "%~dp0index.html"
exit /b 0
