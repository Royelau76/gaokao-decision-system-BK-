@echo off
cd /d "%~dp0"

echo Starting YunZhiXuan...
echo.

REM --- Kill old processes ---
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8000" ^| find "LISTENING" 2^>nul') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| find ":3000" ^| find "LISTENING" 2^>nul') do taskkill /f /pid %%a >nul 2>&1

REM --- Check deps ---
python -c "import fastapi" 2>nul || pip install -r backend\requirements.txt
if not exist "frontend\node_modules" (cd frontend && call npm install --legacy-peer-deps && cd ..)

REM --- Start backend ---
start "Backend" cmd /c "cd /d %~dp0backend && python main.py"

REM --- Start frontend ---
start "Frontend" cmd /c "cd /d %~dp0frontend && set BROWSER=none && npm start"

REM --- Open browser after delay ---
echo Waiting 20 seconds for services to start...
timeout /t 20 /nobreak

echo.
echo ========================================
echo   System Ready!
echo   Open in browser: http://localhost:3000
echo   Backend API docs: http://localhost:8000/docs
echo ========================================
echo.
echo Close Backend/Frontend windows to stop.
pause
