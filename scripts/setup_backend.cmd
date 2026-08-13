@echo off
setlocal

cd /d "%~dp0.."

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.10+ from python.org.
  exit /b 1
)

py -3 --version >nul 2>nul
if errorlevel 1 (
  echo Python launcher exists, but Python cannot start.
  echo On Windows, disable Microsoft Store python aliases or install Python 3.10+ from python.org.
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv venv
  if errorlevel 1 exit /b 1
)

echo Installing backend dependencies...
venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1

venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1

if not exist ".env" (
  echo Creating .env from .env.example...
  copy .env.example .env >nul
)

echo Applying migrations...
venv\Scripts\python.exe manage.py migrate
if errorlevel 1 exit /b 1

echo Backend setup complete. Run scripts\check_backend.cmd to verify the project.
