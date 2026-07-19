@echo off
REM ============================================================
REM setup.bat - One-time environment setup for GesturePPT
REM ============================================================

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ============================================================
echo Setup complete! Use run.bat to start GesturePPT.
echo ============================================================
pause
