@echo off
setlocal enabledelayedexpansion
title RAG Document Intelligence - Windows 11 Launcher

echo ==============================================================================
echo       RAG DOCUMENT INTELLIGENCE - WINDOWS 11 LAUNCHER
echo ==============================================================================
echo.

:: 1. Verify Python Installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.11+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version

:: 2. Verify Node.js Installation
echo.
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not found in PATH!
    echo Please install Node.js 20+ from https://nodejs.org/
    pause
    exit /b 1
)
node --version

:: 3. Setup Virtual Environment
echo.
echo [3/6] Setting up Python virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment at .\venv ...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

:: 4. Verify / Install Backend Dependencies
echo.
echo [4/6] Checking Python dependencies...
python -c "import fastapi, chromadb, sentence_transformers" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing backend dependencies from backend\requirements.txt ...
    pip install -r backend\requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
) else (
    echo Backend dependencies are verified.
)

:: Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example ...
        copy .env.example .env >nul
    )
)

:: 5. Verify / Install Frontend Dependencies
echo.
echo [5/6] Checking Frontend npm packages...
if not exist "frontend\node_modules" (
    echo Installing frontend packages...
    cd frontend
    call npm install
    cd ..
) else (
    echo Frontend node_modules are verified.
)

:: 6. Launch Backend and Frontend in Dedicated Windows
echo.
echo [6/6] Launching services...
echo.
echo ------------------------------------------------------------------------------
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "RAG Backend Server (Port 8000)" cmd /k "call venv\Scripts\activate.bat && cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting Vite Frontend on http://localhost:5173 ...
start "RAG Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo Waiting for services to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ==============================================================================
echo   RAG Document Intelligence is now running!
echo   - Backend:  http://127.0.0.1:8000
echo   - Frontend: http://localhost:5173
echo   - API Docs: http://127.0.0.1:8000/docs
echo.
echo   To stop the application, close the two terminal windows.
echo ==============================================================================
pause
