# Aplicación de Mensajería Cifrada con RSA

Aplicación web para enviar mensajes cifrados usando RSA en una red local.

## Instalación

### 1. Requisitos
- Python 3.7 o superior
- Pip (gestor de paquetes de Python)

Verificar instalación:
```bash
python --version
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Dependencias que se instalan:
- Flask: Framework web
- Flask-CORS: Permitir peticiones entre diferentes IPs
- Cryptography: Librería de cifrado RSA
- Requests: Envío de mensajes HTTP

### 3. Configurar Firewall (IMPORTANTE)

Para que otras computadoras puedan conectarse, debes habilitar el puerto en el firewall:

**Windows - Ejecutar como Administrador:**
```bash
netsh advfirewall firewall add rule name="Flask Port 5000" dir=in action=allow protocol=TCP localport=5000
```

**Alternativa - Permitir Python:**
```bash
netsh advfirewall firewall add rule name="Python Flask" dir=in action=allow program="C:\Path\To\Python\python.exe" enable=yes
```
(Ajustar la ruta de python.exe según tu instalación)

### 4. Cerrar puerto del Firewall (Después de usar)

**IMPORTANTE:** Por seguridad, cuando termines de usar la aplicación, cierra el puerto del firewall:

**Eliminar la regla del puerto 5000:**
```bash
netsh advfirewall firewall delete rule name="Flask Port 5000"
```

**Eliminar la regla de Python:**
```bash
netsh advfirewall firewall delete rule name="Python Flask"
```

**Verificar que se eliminó:**
```bash
netsh advfirewall firewall show rule name="Flask Port 5000"
```
Debe mostrar: "No rules match the specified criteria"

---

## Uso

### 1. Iniciar la aplicación

```bash
python app.py
```

La aplicación se inicia en: http://localhost:5000

Al iniciar verás tus direcciones IP disponibles:
```
Direcciones IP disponibles para compartir:

  1. 192.168.1.100   - Red Local (WiFi/Ethernet)
  2. 10.147.20.45    - Red Local / ZeroTier
```

### 2. Acceder a la interfaz web

**Desde la misma computadora:**
```
http://localhost:5000
```

**Desde otra computadora en la red:**
```
http://[TU_IP]:5000
```
Ejemplo: http://192.168.1.100:5000

### 3. Generar claves

1. Abre la aplicación en tu navegador
2. Click en "Generar Nuevas Claves"
3. Tu clave pública aparecerá en pantalla
4. Las claves se guardan automáticamente en:
   - private_key.pem (NUNCA compartir)
   - public_key.pem (compartir libremente)

### 4. Enviar mensajes

**Método 1 - Obtención automática (Recomendado):**
1. Ingresa la IP del destinatario
2. Click en "Obtener Clave"
3. La aplicación obtiene automáticamente la clave pública
4. Escribe tu mensaje
5. Click en "Enviar Mensaje Cifrado"

**Método 2 - Manual:**
1. Pide al destinatario su clave pública
2. Ingresa su IP
3. Pega su clave pública en el campo correspondiente
4. Escribe tu mensaje
5. Click en "Enviar Mensaje Cifrado"

### 5. Recibir mensajes

Los mensajes se reciben y descifran automáticamente.
- Se muestran en la sección "Mensajes Recibidos"
- Se actualizan cada 5 segundos
- Puedes actualizar manualmente con el botón "Actualizar Mensajes"

---

## Uso con ZeroTier

ZeroTier permite conectar computadoras en diferentes ubicaciones físicas como si estuvieran en la misma red.

### Configuración:

1. Instalar ZeroTier en todos los dispositivos
2. Crear una red en ZeroTier Central (https://my.zerotier.com)
3. Unir todos los dispositivos a la misma red ZeroTier
4. Usar la IP de ZeroTier (comienza con 10.x.x.x)

### Ventajas:
- Conecta dispositivos en diferentes ubicaciones
- Conexión cifrada a nivel de red
- No requiere configurar routers
- Funciona como red local virtual

### Ejemplo:

**Computadora A (Casa):**
- IP Local: 192.168.0.100
- IP ZeroTier: 10.147.20.45
- Comparte: 10.147.20.45

**Computadora B (Oficina):**
- IP Local: 192.168.1.200
- IP ZeroTier: 10.147.20.78
- Para enviar a A usa: 10.147.20.45

---

## Contactos Guardados

La aplicación guarda automáticamente los contactos que uses:
- Se almacenan en el navegador (localStorage)
- Incluyen: IP, puerto y clave pública
- Puedes seleccionarlos con un click
- Se pueden eliminar individualmente

---

## Estructura del Proyecto

```
AppMensajeria/
├── app.py                 # Servidor Flask principal
├── crypto_utils.py        # Utilidades de cifrado RSA
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── templates/
│   └── index.html        # Interfaz web
├── private_key.pem       # Clave privada (generada automáticamente)
└── public_key.pem        # Clave pública (generada automáticamente)
```

---

## Solución de Problemas

### Error: "Failed to fetch"
**Causa:** Falta configurar CORS o el firewall bloquea la conexión

**Solución:**
1. Verificar que flask-cors está instalado:
   ```bash
   pip install flask-cors
   ```
2. Habilitar puerto en firewall (ver sección Instalación)
3. Reiniciar la aplicación

### Error: "Error de conexión"
**Verificar:**
- Ambas computadoras en la misma red
- Firewall permite el puerto 5000
- IP correcta
- Aplicación del destinatario está corriendo

**Probar conectividad:**
```bash
ping [IP_DESTINATARIO]
```

### Error: "No se pudo obtener la clave pública"
**Verificar:**
- La aplicación está corriendo en la IP destino
- Firewall no bloquea
- IP correcta (sin espacios extras)

### Verificar puerto abierto:
```bash
netstat -an | findstr :5000
```
Debe mostrar: TCP 0.0.0.0:5000 LISTENING

---

## Seguridad

### Cifrado:
- RSA 2048 bits (estándar industrial)
- Cifrado de extremo a extremo
- Solo el destinatario puede descifrar

### Claves:
- Clave privada: NUNCA sale de tu computadora
- Clave pública: Se puede compartir libremente
- Las claves se generan localmente

### Firewall:
- Abrir puerto SOLO cuando uses la aplicación
- Cerrar puerto cuando termines de usar
- Evita dejar puertos abiertos innecesariamente
- Reduce riesgo de infiltraciones

### IMPORTANTE:
- NO compartir el archivo private_key.pem
- NO enviar la clave privada por ningún medio
- Solo compartir la clave pública
- CERRAR el puerto del firewall después de usar:
  ```bash
  netsh advfirewall firewall delete rule name="Flask Port 5000"
  ```

---

## Conceptos de Criptografía

### RSA (Algoritmo de cifrado asimétrico)

**Clave Pública:**
- Se comparte libremente
- Sirve para CIFRAR mensajes
- Cualquiera puede cifrar con ella

**Clave Privada:**
- Se mantiene secreta
- Sirve para DESCIFRAR mensajes
- Solo tú puedes descifrar

### Flujo de comunicación:

1. Alice y Bob generan sus pares de claves
2. Intercambian claves públicas
3. Alice cifra mensaje con clave pública de Bob
4. Bob descifra mensaje con su clave privada
5. Solo Bob puede leer el mensaje

---

## Comandos Útiles

### Verificar IP:
```bash
ipconfig                    # Windows
ip addr                     # Linux
ifconfig                    # Mac
```

### Probar conectividad:
```bash
ping [IP_DESTINO]
```

### Ver puertos en uso:
```bash
netstat -an | findstr :5000  # Windows
netstat -an | grep 5000      # Linux/Mac
```

### Detener la aplicación:
```
Ctrl + C
```

### Gestión del Firewall:

**Abrir puerto:**
```bash
netsh advfirewall firewall add rule name="Flask Port 5000" dir=in action=allow protocol=TCP localport=5000
```

**Cerrar puerto:**
```bash
netsh advfirewall firewall delete rule name="Flask Port 5000"
```

**Listar reglas del firewall:**
```bash
netsh advfirewall firewall show rule name=all | findstr "Flask"
```

**Ver estado de una regla específica:**
```bash
netsh advfirewall firewall show rule name="Flask Port 5000"
```

---

## Ejemplo Completo

### Escenario: Dos computadoras en la misma red

**Computadora A (192.168.1.100):**
1. Ejecutar: python app.py
2. Generar claves
3. Compartir:
   - IP: 192.168.1.100
   - Clave pública (copiar desde la interfaz)

**Computadora B (192.168.1.101):**
1. Ejecutar: python app.py
2. Generar claves
3. Abrir navegador: http://localhost:5000
4. En "IP del Destinatario": 192.168.1.100
5. Click "Obtener Clave" (obtiene automáticamente)
6. Escribir mensaje: "Hola desde B"
7. Click "Enviar Mensaje Cifrado"

**Resultado en A:**
- Mensaje aparece automáticamente en "Mensajes Recibidos"
- Mensaje ya descifrado y legible

---

## Tecnologías

- Python 3
- Flask (framework web)
- Flask-CORS (peticiones cross-origin)
- Cryptography (cifrado RSA)
- HTML/CSS/JavaScript (interfaz)

---

## Licencia

Proyecto de código abierto para uso educativo.

## Autor

Creado para el curso de Ciberseguridad - Universidad
