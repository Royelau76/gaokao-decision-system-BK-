@echo off
chcp 65001 >nul
echo ========================================
echo   云志选 - 云南高考志愿决策系统
echo   2026 Windows 启动脚本
echo ========================================
echo.

REM --- Check Python ---
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)
echo [OK] Python found

REM --- Install backend dependencies ---
echo [INFO] Installing backend dependencies...
python -m pip install -r backend\requirements.txt -q 2>nul
echo [OK] Backend dependencies ready

REM --- Start backend in a new window ---
echo [INFO] Starting backend on http://localhost:8000 ...
start "云志选-后端" cmd /c "cd /d %~dp0backend && python main.py"
echo [OK] Backend started in new window
echo       API docs: http://localhost:8000/docs

REM --- Check Node.js ---
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Node.js not found, skipping frontend
    echo        Backend running at http://localhost:8000
    pause
    exit /b 0
)
echo [OK] Node.js found

REM --- Install frontend dependencies ---
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies (npm install)...
    cd frontend
    call npm install
    cd ..
)
echo [OK] Frontend dependencies ready

REM --- Start frontend in a new window ---
echo [INFO] Starting frontend on http://localhost:3000 ...
start "云志选-前端" cmd /c "cd /d %~dp0frontend && npm start"
echo [OK] Frontend started in new window

echo.
echo ========================================
echo   System ready!
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API:  http://localhost:8000/docs
echo ========================================
echo.
echo Close this window or the backend/frontend windows to stop.
pause
