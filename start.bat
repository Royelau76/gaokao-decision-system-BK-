@echo off
chcp 65001 >nul
title 云志选 - 启动

echo ========================================
echo   云志选 - 云南高考志愿决策系统
echo ========================================
echo.

REM --- Kill existing processes on ports ---
echo [INFO] 检查端口占用...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do (
    echo   关闭占用8000端口的进程 %%a
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000.*LISTENING" 2^>nul') do (
    echo   关闭占用3000端口的进程 %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo [OK] 端口已清理
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
echo [INFO] 安装后端依赖...
pip install -r backend\requirements.txt -q 2>nul
echo [OK] 后端依赖就绪

REM --- Start backend ---
echo [INFO] 启动后端 (http://localhost:8000) ...
start "云志选-后端" cmd /k "cd /d %~dp0backend && python main.py && pause"
echo [OK] 后端已在新窗口启动
echo       API 文档: http://localhost:8000/docs
echo.

REM --- Check Node.js ---
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Node.js 未安装, 跳过前端
    echo       后端已启动: http://localhost:8000
    pause
    exit /b 0
)
echo [OK] Node.js found

REM --- Install frontend dependencies ---
if not exist "frontend\node_modules" (
    echo [INFO] 安装前端依赖 (npm install --legacy-peer-deps) ...
    cd frontend
    call npm install --legacy-peer-deps
    cd ..
)
echo [OK] 前端依赖就绪

REM --- Start frontend ---
echo [INFO] 启动前端 (http://localhost:3000) ...
start "云志选-前端" cmd /k "cd /d %~dp0frontend && npm start && pause"
echo [OK] 前端已在新窗口启动

echo.
echo ========================================
echo   系统启动完成！
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API:  http://localhost:8000/docs
echo ========================================
echo.
echo 关闭后端/前端窗口即可停止服务.
pause
