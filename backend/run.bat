@echo off
setlocal

REM NHAA Case API - Run Script
REM Usage: run.bat [start|test|migrate]

if "%1"=="" (
    set ACTION=start
) else (
    set ACTION=%1
)

cd /d "%~dp0"

REM Activate venv
call .venv\Scripts\activate.bat

if "%ACTION%"=="start" (
    echo Starting NHAA Case API on http://localhost:8000 ...
    echo Swagger UI: http://localhost:8000/docs
    echo.
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
)

if "%ACTION%"=="test" (
    echo Running synchronization test ...
    python -m pytest tests/test_sync.py -v -s
)

if "%ACTION%"=="migrate" (
    echo Running Alembic migrations ...
    python -m alembic upgrade head
)

if "%ACTION%"=="makemigrations" (
    echo Generating migration ...
    python -m alembic revision --autogenerate -m "%2"
)
