# Solución: Error "Failed to fetch"

## Problema
Al intentar obtener la clave pública de otra IP aparece:
```
Error de conexión: Failed to fetch
```

## Causa
Este error ocurre porque falta configurar **CORS** (Cross-Origin Resource Sharing) en Flask, lo que impide que el navegador haga peticiones a otras IPs.

---

## Solución Implementada

### 1. CORS Agregado
He agregado `flask-cors` para permitir peticiones entre diferentes IPs.

### 2. Pasos para Aplicar la Solución

#### Paso 1: Detener la aplicación
Si está corriendo, presiona `Ctrl+C` en la terminal.

#### Paso 2: Instalar la nueva dependencia
```bash
pip install flask-cors
```

O reinstalar todas las dependencias:
```bash
pip install -r requirements.txt
```

#### Paso 3: Verificar Firewall de Windows

**Opción A - Permitir Python en Firewall:**
```bash
netsh advfirewall firewall add rule name="Python Flask" dir=in action=allow program="C:\Python\python.exe" enable=yes
```
(Ajusta la ruta de python.exe según tu instalación)

**Opción B - Permitir Puerto 5000:**
```bash
netsh advfirewall firewall add rule name="Flask Port 5000" dir=in action=allow protocol=TCP localport=5000
```

**Opción C - Desactivar Firewall temporalmente (solo para pruebas):**
1. Windows + R
2. Escribir: `firewall.cpl`
3. Click en "Activar o desactivar Firewall de Windows Defender"
4. Desactivar para red privada

#### Paso 4: Reiniciar la aplicación
```bash
python app.py
```

---

## Verificación

### Test 1: Verificar que CORS está activo
Al iniciar la app, deberías ver que responde correctamente.

### Test 2: Probar desde la misma computadora
1. Abre `http://localhost:5000`
2. En "Obtener Clave", usa tu propia IP
3. Debería obtener tu clave sin problemas

### Test 3: Probar desde otra computadora
1. Desde otra PC en la red, abre `http://[IP_PRIMERA_PC]:5000`
2. Usa el botón "Obtener Clave" con la IP de la primera PC
3. Debería funcionar

---

## Otras Causas Posibles

### 1. Ambas computadoras no están en la misma red
**Verificar:**
```bash
ipconfig
```
Ambas IPs deben estar en el mismo rango (ej: 192.168.1.x)

**Solución:**
- Conectar ambas al mismo WiFi
- O usar ZeroTier para conectarlas

### 2. Antivirus bloqueando
**Solución:**
Agregar excepción para Python o el puerto 5000 en tu antivirus.

### 3. Proxy o VPN activa
**Solución:**
Desactivar proxy/VPN temporalmente para pruebas.

---

## Probar Conectividad

### Paso 1: Ping entre computadoras
Desde una computadora, hacer ping a la otra:
```bash
ping 192.168.1.100
```

Si responde, la red está bien.

### Paso 2: Verificar puerto abierto
Desde la computadora A (donde corre la app), verifica que el puerto está escuchando:
```bash
netstat -an | findstr :5000
```

Debería mostrar:
```
TCP    0.0.0.0:5000    LISTENING
```

### Paso 3: Probar con curl (si tienes Git Bash)
```bash
curl http://192.168.1.100:5000/api/get-public-key
```

Debería devolver la clave pública en JSON.

---

## Resumen de Cambios Realizados

### Archivo: requirements.txt
```diff
flask==3.0.0
+ flask-cors==4.0.0
cryptography==41.0.7
requests==2.31.0
```

### Archivo: app.py
```diff
from flask import Flask, render_template, request, jsonify
+ from flask_cors import CORS
import requests
import os
import socket
from crypto_utils import CryptoManager

app = Flask(__name__)
+ CORS(app)
crypto_manager = CryptoManager()
```

---

## Checklist de Solución

- [ ] Instalar flask-cors: `pip install flask-cors`
- [ ] Reiniciar la aplicación
- [ ] Verificar que el firewall permite Python o puerto 5000
- [ ] Probar con IP propia primero
- [ ] Probar desde otra computadora
- [ ] Verificar que ambas están en la misma red

---

## Ejemplo de Configuración Exitosa

### Computadora A (192.168.1.100)
```bash
python app.py

Claves cargadas desde archivos existentes

============================================================
  Aplicación de Mensajería Cifrada RSA
============================================================

Direcciones IP disponibles para compartir:

  1. 192.168.1.100   - Red Local (WiFi/Ethernet)

============================================================
Acceso Local:  http://localhost:5000
Acceso Remoto: Usa cualquiera de las IPs mostradas arriba
               Ejemplo: http://[IP]:5000
============================================================
```

### Computadora B (192.168.1.101)
1. Abre: `http://localhost:5000` (su propia app)
2. En "IP del Destinatario": `192.168.1.100`
3. Click "Obtener Clave"
4. Resultado: Clave obtenida correctamente

---

## Si Sigue Sin Funcionar

### Debug desde el navegador:
1. Presiona F12
2. Ve a la pestaña "Console"
3. Intenta obtener la clave
4. Verás el error específico

### Errores comunes:

**"ERR_CONNECTION_REFUSED"**
- La app no está corriendo en esa IP
- Firewall bloqueando

**"ERR_CONNECTION_TIMED_OUT"**
- No están en la misma red
- Firewall muy restrictivo

**"CORS policy"**
- CORS no está configurado (ya lo arreglamos)

**"net::ERR_NAME_NOT_RESOLVED"**
- IP incorrecta o mal escrita

---

## Solución Rápida (Para Desarrolladores)

Si estás probando localmente en la misma computadora:
```bash
# En lugar de usar tu IP, usa:
http://localhost:5000

# O
http://127.0.0.1:5000
```

Esto evita problemas de red/firewall para pruebas iniciales.

---

## Comando Único para Probar

Crea un archivo `test_connection.py`:
```python
import requests

ip = "192.168.1.100"  # Cambia por la IP a probar
port = 5000

try:
    response = requests.get(f"http://{ip}:{port}/api/get-public-key", timeout=5)
    if response.status_code == 200:
        print("Conexión exitosa")
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error de conexión: {e}")
```

Ejecuta:
```bash
python test_connection.py
```

Si funciona, el problema es del navegador/CORS (ya solucionado).
Si no funciona, el problema es de red/firewall.

---

¡Con CORS configurado, el error debería estar resuelto!
