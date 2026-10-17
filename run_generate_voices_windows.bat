@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [MOVE CLOCK] Generate BOTH female F1 and male M1 Supertonic voices.
echo Initial model download: around 400 MB. A Windows Python 3.10+ is required.
where py >nul 2>&1
if %errorlevel% neq 0 (
  echo Python Launcher is missing. Install Python 3.10+.
  pause
  exit /b 1
)
py -m pip install supertonic
if errorlevel 1 (
  echo Supertonic installation failed.
  pause
  exit /b 1
)
py generate_supertonic.py
if errorlevel 1 (
  echo Voice generation failed. Review the error above.
  pause
  exit /b 1
)
echo Done. Upload voices/ to GitHub if GitHub Actions did not do so.
pause
