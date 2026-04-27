@echo off
title YunZhiXuan - Startup

echo ========================================
echo   YunZhiXuan - Gaokao Decision System
echo ========================================
echo.

REM --- Kill existing processes on ports ---
echo [INFO] Checking port usage...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do (
    echo   Stopping process on port 8000: %%a
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000.*LISTENING" 2^>nul') do (
    echo   Stopping process on port 3000: %%a
    taskkill /F /PID %%a >nul 2>&1
)
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
echo [INFO] Installing backend dependencies...
pip install -r backend\requirements.txt -q 2>nul
echo [OK] Backend dependencies ready

REM --- Start backend ---
echo [INFO] Starting backend (http://localhost:8000) ...
start "Backend" cmd /k "cd /d %~dp0backend && python main.py && pause"
echo [OK] Backend started in new window
echo       API docs: http://localhost:8000/docs
echo.

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

REM --- Start frontend ---
echo [INFO] Starting frontend (http://localhost:3000) ...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm start && pause"
echo [OK] Frontend started in new window

echo.
echo ========================================
echo   System Ready!
echo   Frontend : http://localhost:3000
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo ========================================
echo.
echo Close backend/frontend windows to stop.
pause
