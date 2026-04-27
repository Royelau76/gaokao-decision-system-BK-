@echo off
title YunZhiXuan - Startup

echo ========================================
echo   YunZhiXuan - Gaokao Decision System
echo ========================================
echo.

REM --- Kill existing processes on ports ---
echo [1/5] Checking port usage...
powershell -NoProfile -Command "netstat -ano|Select-String ':8000.*LISTENING'|ForEach-Object{stop-process -id ((-split$_)[-1]) -force -erroraction silentlycontinue}" 2>nul
powershell -NoProfile -Command "netstat -ano|Select-String ':3000.*LISTENING'|ForEach-Object{stop-process -id ((-split$_)[-1]) -force -erroraction silentlycontinue}" 2>nul
echo       Done.

REM --- Check Python & dependencies ---
echo [2/5] Checking Python...
where python >nul 2>&1 || (echo Python not found && pause && exit /b 1)
python -c "import fastapi,uvicorn,pydantic" 2>nul || pip install -r backend\requirements.txt
echo       Done.

REM --- Start backend ---
echo [3/5] Starting backend...
start "YunZhiXuan-Backend" cmd /k "title 云志选-后端 %~dp0backend && python main.py"
echo       Backend: http://localhost:8000

REM --- Check Node.js & dependencies ---
echo [4/5] Checking Node.js...
where node >nul 2>&1 || (echo Node.js not found, backend only && pause && exit /b 0)
if not exist "frontend\node_modules" (cd frontend && call npm install --legacy-peer-deps && cd ..)
echo       Done.

REM --- Start frontend ---
echo [5/5] Starting frontend...
start "YunZhiXuan-Frontend" cmd /k "title 云志选-前端 && cd /d %~dp0frontend && set BROWSER=none && npm start"
echo       Frontend: http://localhost:3000

REM --- Wait and open browser ---
echo.
echo Waiting for services to start (about 30s)...
echo.
timeout /t 25 /nobreak >nul
echo Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo   System Ready!
echo   Frontend : http://localhost:3000
echo   Backend  : http://localhost:8000
echo ========================================
echo.
echo Close the Backend/Frontend windows to stop.
pause
