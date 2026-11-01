@echo off
setlocal
cd /d "%~dp0"
echo.
echo ================================================
echo  SAHAYAKA - Multilingual Government Scheme Help
echo ================================================
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js is not installed. Install Node.js 20 LTS or newer from https://nodejs.org and rerun this file.
  pause
  exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: npm was not found. Reinstall Node.js with npm enabled.
  pause
  exit /b 1
)

REM Automated port hygiene check (FAULT-08)
echo Checking port availability (8000, 3000, 8501)...
python scripts\clean_ports.py --check-only 2>nul

REM Python runtime setup (FAULT-01)
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -3.11 -m venv .venv 2>nul
  if errorlevel 1 py -3.12 -m venv .venv 2>nul
  if errorlevel 1 py -3.14 -m venv .venv 2>nul
  if errorlevel 1 py -3 -m venv .venv 2>nul
  if errorlevel 1 python -m venv .venv
  if errorlevel 1 (
    echo ERROR: Python was not found. Install Python 3.11+ and rerun.
    pause
    exit /b 1
  )
)

if not exist ".env" (
  echo Creating local configuration from template...
  copy /Y ".env.example" ".env" >nul
)

echo Installing/checking backend runtime dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements-local.txt
if errorlevel 1 (
  echo WARNING: Using existing packages or fallback. Continuing...
)

if not exist "frontend-web\node_modules" (
  echo Installing frontend dependencies - this may take a few minutes...
  pushd frontend-web
  call npm install
  if errorlevel 1 (
    popd
    echo ERROR: Frontend dependencies failed to install. Check internet access and npm output.
    pause
    exit /b 1
  )
  popd
)

echo Checking Ollama availability...
ollama list >nul 2>nul
if errorlevel 1 (
  echo WARNING: Ollama CLI was not found. Sahayaka will use deterministic fallback.
)

echo Starting FastAPI backend in a new window...
start "Sahayaka API" /D "%~dp0" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

echo Starting Next.js frontend in a new window...
start "Sahayaka Web UI" /D "%~dp0frontend-web" cmd /k "npm run dev"

echo.
echo App ready at http://localhost:3000 after Next.js starts.
echo API docs: http://127.0.0.1:8000/api/v1/docs
echo Keep terminal windows open while using the app.
timeout /t 5 >nul
start "" http://localhost:3000
endlocal
