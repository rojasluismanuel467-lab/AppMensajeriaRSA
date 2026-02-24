@echo off
echo ========================================
echo   Mensajeria Segura con RSA
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
pip install -r requirements.txt -q

echo.
echo Iniciando aplicacion...
echo.

REM Iniciar aplicacion
python main.py

pause
