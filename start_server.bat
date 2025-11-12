@echo off
echo ========================================
echo   DEMARRAGE DU SERVEUR SIEM
echo ========================================
echo.

cd serveur

echo Verification des dependances...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
)

echo.
echo Demarrage du serveur...
echo.
python app.py

pause

