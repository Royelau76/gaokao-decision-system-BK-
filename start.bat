@echo off
title YunZhiXuan - Startup

echo ========================================
echo   YunZhiXuan - Gaokao Decision System
echo ========================================
echo.

REM --- Kill existing processes on ports ---
echo [INFO] Checking port usage...
powershell -NoProfile -Command "netstat -ano|Select-String ':8000.*LISTENING'|ForEach-Object{stop-process -id ((-split$_)[-1]) -force -erroraction silentlycontinue}" 2>nul
powershell -NoProfile -Command "netstat -ano|Select-String ':3000.*LISTENING'|ForEach-Object{stop-process -id ((-split$_)[-1]) -force -erroraction silentlycontinue}" 2>nul
echo [OK] Ports cleared
echo.

REM --- Check Python ---
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Python not found
    pause
    exit /b 1
)
echo [OK] Python found

REM --- Install backend dependencies ---
echo [INFO] Checking backend dependencies...
python -c "import fastapi, uvicorn, pydantic" 2>nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Backend dependencies already installed
) else (
    echo [INFO] Installing backend dependencies...
    pip install -r backend\requirements.txt
    echo [OK] Backend dependencies installed
)
echo.

REM --- Start backend ---
echo [INFO] Starting backend on http://localhost:8000 ...
start "Backend" /MIN cmd /c "cd /d %~dp0backend && python main.py"
echo [OK] Backend starting...

REM --- Check Node.js ---
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Node.js not found, skipping frontend
    echo       Backend: http://localhost:8000
    pause
    exit /b 0
)
echo [OK] Node.js found

REM --- Install frontend dependencies ---
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies (npm install --legacy-peer-deps) ...
    cd frontend
    call npm install --legacy-peer-deps
    cd ..
)
echo [OK] Frontend dependencies ready
echo.

REM --- Start frontend ---
echo [INFO] Starting frontend on http://localhost:3000 ...
start "Frontend" /MIN cmd /c "cd /d %~dp0frontend && npm start"
echo [OK] Frontend starting...

REM --- Wait for services to be ready ---
echo.
echo [INFO] Waiting for services to start...
echo        (this may take 30-60 seconds on first run)
:wait_backend
timeout /t 3 /nobreak >nul
powershell -NoProfile -Command "try{$r=Invoke-WebRequest -Uri http://localhost:8000 -TimeoutSec 2 -UseBasicParsing;exit 0}catch{exit 1}" 2>nul
if %ERRORLEVEL% neq 0 goto wait_backend
echo [OK] Backend ready

:wait_frontend
timeout /t 3 /nobreak >nul
powershell -NoProfile -Command "try{$r=Invoke-WebRequest -Uri http://localhost:3000 -TimeoutSec 2 -UseBasicParsing;exit 0}catch{exit 1}" 2>nul
if %ERRORLEVEL% neq 0 goto wait_frontend
echo [OK] Frontend ready

REM --- Open browser ---
echo.
echo [INFO] Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo   System Ready!
echo   Frontend : http://localhost:3000
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo ========================================
echo.
echo Backend/Frontend running in minimized windows.
echo Close them from taskbar to stop the system.
pause
