@echo off
echo ========================================
echo   Gestion de Firewall - Puerto 5000
echo ========================================
echo.
echo 1. Abrir puerto 5000
echo 2. Cerrar puerto 5000
echo 3. Verificar estado del puerto
echo 4. Salir
echo.
choice /c 1234 /n /m "Selecciona una opcion: "

if errorlevel 4 goto :salir
if errorlevel 3 goto :verificar
if errorlevel 2 goto :cerrar
if errorlevel 1 goto :abrir

:abrir
echo.
echo Abriendo puerto 5000...
netsh advfirewall firewall add rule name="Flask Port 5000" dir=in action=allow protocol=TCP localport=5000
echo.
echo Puerto 5000 ABIERTO
pause
goto :menu

:cerrar
echo.
echo Cerrando puerto 5000...
netsh advfirewall firewall delete rule name="Flask Port 5000"
echo.
echo Puerto 5000 CERRADO
pause
goto :menu

:verificar
echo.
echo Verificando estado del puerto 5000...
netsh advfirewall firewall show rule name="Flask Port 5000"
echo.
pause
goto :menu

:salir
exit

:menu
cls
goto :eof
