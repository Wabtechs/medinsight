@echo off
echo ============================================
echo   MedInsight Backend - Local SQLite Mode
echo ============================================
echo.

cd /d "%~dp0"

if not exist ".env" (
    echo Copying .env.local to .env...
    copy .env.local .env
)

echo Starting FastAPI on http://localhost:8000
echo Database: SQLite (local)
echo Docs: http://localhost:8000/docs
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
