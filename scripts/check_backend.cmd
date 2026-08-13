@echo off
setlocal

cd /d "%~dp0.."

set "PYTHON_EXE="

if exist "venv\Scripts\python.exe" (
  set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=py -3"
)

if "%PYTHON_EXE%"=="" (
  echo Python was not found. Install Python 3.10+ and run scripts\setup_backend.cmd.
  exit /b 1
)

%PYTHON_EXE% --version >nul 2>nul
if errorlevel 1 (
  echo Python was found but could not start.
  echo On Windows, disable the Microsoft Store python aliases or install Python 3.10+ from python.org.
  echo Then run scripts\setup_backend.cmd.
  exit /b 1
)

echo Running Django system checks...
%PYTHON_EXE% manage.py check
if errorlevel 1 exit /b 1

echo Running Django tests...
%PYTHON_EXE% manage.py test
if errorlevel 1 exit /b 1

echo Backend checks passed.
