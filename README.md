# 🔐 Aplicación de Mensajería Cifrada con RSA

Aplicación web sencilla para enviar mensajes cifrados usando RSA en una red local.

## 📋 Características

- ✅ Interfaz web intuitiva y moderna
- ✅ Generación automática de claves RSA (2048 bits)
- ✅ Cifrado de extremo a extremo
- ✅ Comunicación en red local
- ✅ Recepción automática de mensajes
- ✅ Visualización de mensajes descifrados

## 🚀 Instalación

### 1. Instalar Python

Asegúrate de tener Python 3.7 o superior instalado:
```bash
python --version
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Las librerías que se instalarán son:
- **Flask**: Framework web para la interfaz
- **cryptography**: Librería de cifrado RSA
- **requests**: Para enviar mensajes HTTP

## 💻 Uso

### 1. Iniciar la aplicación

```bash
python app.py
```

La aplicación se iniciará en `http://localhost:5000`

### 2. Acceder desde otra computadora

Para que otros dispositivos en tu red puedan comunicarse contigo:

1. **La aplicación detecta automáticamente todas tus IPs** al iniciar:
   - Verás todas las direcciones IP disponibles en la consola
   - También se mostrarán en la interfaz web

2. **Tipos de IPs que puedes ver:**
   - **192.168.x.x** - Red WiFi/Ethernet local
   - **10.x.x.x** - Generalmente ZeroTier u otras VPNs
   - **172.16.x.x a 172.31.x.x** - Redes privadas

3. Otros usuarios pueden acceder a tu aplicación usando:
   ```
   http://[TU_IP]:5000
   ```

### 3. Uso con ZeroTier

Si usas ZeroTier para crear una red virtual privada:

1. **Instala ZeroTier** en todos los dispositivos que quieras conectar
2. **Une todos los dispositivos a la misma red ZeroTier**
3. **Usa la IP de ZeroTier (generalmente 10.x.x.x)** para conectarte:
   - La aplicación identificará automáticamente tu IP de ZeroTier
   - Comparte esta IP con otros usuarios en tu red ZeroTier
   - Funciona incluso si los dispositivos están en diferentes redes físicas

**Ventajas de ZeroTier:**
- ✅ Conecta dispositivos en diferentes ubicaciones físicas
- ✅ Conexión segura y cifrada a nivel de red
- ✅ No necesitas abrir puertos en tu router
- ✅ Funciona como si estuvieras en la misma red local

### 4. Enviar un mensaje cifrado

1. **Generar tus claves**: Click en "Generar Nuevas Claves"
2. **Compartir tu información**:
   - Copia tu clave pública
   - Comparte una de tus direcciones IP (mostradas en la interfaz)
   - Si usas ZeroTier, comparte la IP que empieza con 10.x.x.x
3. **Obtener la información del destinatario**: Pide su clave pública e IP
4. **Enviar mensaje**:
   - Ingresa la IP del destinatario
   - Pega su clave pública
   - Escribe tu mensaje
   - Click en "Enviar Mensaje Cifrado"

### 5. Recibir mensajes

- Los mensajes se reciben y descifran automáticamente
- Se actualizan cada 5 segundos
- Puedes hacer click en "Actualizar Mensajes" para verlos inmediatamente

## 🔒 Seguridad

- **Cifrado RSA 2048 bits**: Nivel de seguridad estándar industrial
- **Claves privadas locales**: Tu clave privada NUNCA sale de tu computadora
- **Las claves se guardan en archivos locales**: `private_key.pem` y `public_key.pem`
- **⚠️ IMPORTANTE**: NO compartas tu archivo `private_key.pem` con nadie

## 📁 Estructura del Proyecto

```
AppMensajeria/
│
├── app.py                 # Servidor Flask principal
├── crypto_utils.py        # Utilidades de cifrado RSA
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
│
├── templates/
│   └── index.html        # Interfaz web
│
├── private_key.pem       # Tu clave privada (generada automáticamente)
└── public_key.pem        # Tu clave pública (generada automáticamente)
```

## 🛠️ Tecnologías Utilizadas

- **Python 3**: Lenguaje de programación
- **Flask**: Framework web
- **cryptography**: Librería de cifrado
- **HTML/CSS/JavaScript**: Interfaz web

## 📝 Ejemplos de Uso

### Escenario 1: Dos computadoras en la misma red WiFi

**Computadora A (192.168.1.100)**:
1. Ejecuta `python app.py`
2. Ve sus IPs disponibles (192.168.1.100)
3. Genera claves y comparte la clave pública e IP

**Computadora B (192.168.1.101)**:
1. Ejecuta `python app.py`
2. Genera claves y comparte la clave pública
3. Para enviar mensaje a A:
   - IP: `192.168.1.100`
   - Puerto: `5000`
   - Clave pública: [clave de A]
   - Mensaje: "Hola desde B"

### Escenario 2: Dos computadoras con ZeroTier en ubicaciones diferentes

**Computadora A (casa) - IP ZeroTier: 10.147.20.45**:
1. Tiene ZeroTier instalado y conectado a la red ID: abc123
2. Ejecuta `python app.py`
3. Ve sus IPs: 192.168.0.100 (WiFi) y 10.147.20.45 (ZeroTier)
4. **Comparte la IP de ZeroTier: 10.147.20.45**

**Computadora B (oficina) - IP ZeroTier: 10.147.20.78**:
1. Tiene ZeroTier instalado y conectado a la MISMA red ID: abc123
2. Ejecuta `python app.py`
3. Para enviar mensaje a A:
   - IP: `10.147.20.45` (la IP de ZeroTier de A)
   - Puerto: `5000`
   - Clave pública: [clave de A]
   - ✅ ¡El mensaje llega aunque estén en diferentes ciudades!

## ❓ Solución de Problemas

### Error: "No se pudieron cargar las claves"
- Solución: Click en "Generar Nuevas Claves"

### Error: "Error de conexión"
- Verifica que ambas computadoras estén en la misma red
- Verifica que el firewall no esté bloqueando el puerto 5000
- Verifica que la IP sea correcta

### Error: "Error al descifrar"
- Asegúrate de estar usando la clave pública correcta del destinatario
- Verifica que el destinatario haya generado sus claves

## 🔥 Firewall (Windows)

Si tienes problemas de conexión, permite Python en el firewall:

```bash
netsh advfirewall firewall add rule name="Python Flask" dir=in action=allow program="C:\Path\To\Python\python.exe" enable=yes
```

O desactiva temporalmente el firewall para pruebas (no recomendado para producción).

## 📖 Conceptos de Criptografía

### ¿Qué es RSA?
RSA es un algoritmo de cifrado asimétrico que usa dos claves:
- **Clave Pública**: Se comparte libremente, sirve para CIFRAR mensajes
- **Clave Privada**: Se mantiene secreta, sirve para DESCIFRAR mensajes

### Flujo de Cifrado
1. Alice genera su par de claves (pública/privada)
2. Bob genera su par de claves (pública/privada)
3. Alice y Bob intercambian claves PÚBLICAS
4. Alice cifra un mensaje con la clave PÚBLICA de Bob
5. Bob descifra el mensaje con su clave PRIVADA
6. Solo Bob puede leer el mensaje (ni siquiera Alice puede descifrarlo después de cifrarlo)

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## 👨‍💻 Autor

Creado para el curso de Ciberseguridad - Universidad
