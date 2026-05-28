@echo off
setlocal enabledelayedexpansion

:: Set console colors (Cyan text on Black background for a premium feel)
color 0B

echo =================================================================
echo             CONSTRUCTMIND AI - STARTUP SYSTEM
echo =================================================================
echo.

:: 1. Check Python installation
echo [+] Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Get python version for logging
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [Found] %PYTHON_VERSION%
echo.

:: 2. Check Backend Virtual Environment and Dependencies
echo [+] Checking Backend virtual environment...
cd backend

if not exist venv (
    echo [i] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
) else (
    echo [OK] Virtual environment exists.
)

echo.
echo [+] Checking Backend dependencies...
:: Check if dependencies are already installed by running a python one-liner checking imports
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe -c "import fastapi, uvicorn, sqlalchemy, aiosqlite, pydantic, pydantic_settings, openai, networkx, pandas, openpyxl, pdfplumber, httpx, jinja2, reportlab" >nul 2>&1
) else (
    :: Force check failure if python.exe doesn't exist inside venv
    cmd /c exit 1
)

if %errorlevel% neq 0 (
    echo [i] Some dependencies are missing. Installing from requirements.txt...
    venv\Scripts\pip.exe install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully.
) else (
    echo [OK] All backend requirements are met.
)

echo.

:: 3. Check Frontend Dependencies
cd ..
echo [+] Checking Frontend dependencies...
cd frontend

if not exist node_modules (
    echo [i] node_modules not found. Installing frontend packages...
    echo (This may take a minute...)
    call npm install
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install frontend dependencies.
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Frontend packages installed.
) else (
    echo [OK] Frontend packages are present.
)

cd ..
echo.
echo =================================================================
echo            STARTING CONSTRUCTMIND AI SERVICES
echo =================================================================
echo.

:: Start Backend Server
echo [+] Launching Backend Server on port 8000...
start "ConstructMind Backend (Port 8000)" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: Start Frontend Server
echo [+] Launching Frontend Server on port 3000...
start "ConstructMind Frontend (Port 3000)" cmd /k "cd frontend && call npm run dev"

echo.
echo [i] Waiting for servers to initialize...
timeout /t 5 >nul

echo [+] Opening application in browser...
start http://localhost:3000

echo.
echo =================================================================
echo [SUCCESS] ConstructMind AI is now running!
echo You can close this window. The servers will keep running.
echo =================================================================
echo.
pause
