@echo off
echo ========================================
echo   DEMARRAGE DU CLIENT SIEM
echo ========================================
echo.

cd client

echo Verification des dependances...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
)

echo.
echo Demarrage du client...
echo Appuyez sur Ctrl+C pour arreter
echo.
python client_advanced.py

pause

