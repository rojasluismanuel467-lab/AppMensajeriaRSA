# Aplicación de Mensajería Segura con RSA + Red LAN

Aplicación con **interfaz gráfica moderna** para enviar y recibir mensajes cifrados entre usuarios utilizando el algoritmo **RSA** con cifrado **OAEP (Optimal Asymmetric Encryption Padding)** y **SHA-256**.

**✨ Nueva funcionalidad:** Comunicación en tiempo real a través de red local (LAN).

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![RSA](https://img.shields.io/badge/Cifrado-RSA--OAEP-green.svg)
![Red](https://img.shields.io/badge/Red-LAN-purple.svg)

## ✨ Características

- 🎨 **Interfaz gráfica moderna** con diseño minimalista y modo oscuro
- 🔐 **Cifrado RSA-2048** con OAEP-SHA256
- 🌐 **Comunicación LAN** - envía mensajes a otras PCs en la misma red
- 👥 **Múltiples usuarios** - cada uno con su par de claves
- 📋 **Portapapeles integrado** para copiar/pegar mensajes cifrados
- 🔒 **Protección con contraseña** opcional para claves privadas
- 📨 **Recepción en tiempo real** de mensajes cifrados

## 📦 Instalación

1. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

2. **Ejecuta la aplicación:**

```bash
python main.py
```

## 🚀 Uso Rápido

### Modo Local (Sin Red)

#### 1. Crear un Usuario

1. Abre la aplicación
2. En la pestaña **👤 Usuarios**
3. Ingresa un nombre (ej: `alice`)
4. Opcional: contraseña para proteger la clave
5. Haz clic en **✨ Generar Claves**

#### 2. Enviar Mensaje (Portapapeles)

1. Carga un usuario (ej: `alice`)
2. Ve a la pestaña **💬 Mensajes**
3. Selecciona un destinatario
4. Escribe el mensaje
5. Haz clic en **🔒 Cifrar y Enviar**
6. El mensaje cifrado se copia al portapapeles
7. Envíalo por WhatsApp, email, etc.

---

## 🌐 Comunicación por Red LAN

### ¿Qué necesitas?

- Dos computadoras en la **misma red WiFi/Ethernet**
- Cada PC ejecutando la aplicación
- Claves públicas intercambiadas

### Flujo de Comunicación

```
┌──────────────────┐                          ┌──────────────────┐
│   PC de Alice    │                          │   PC de Bob      │
│   IP: 192.168.1.50                        │   IP: 192.168.1.100
│                  │                          │                  │
│  1. Iniciar      │                          │  1. Iniciar      │
│     Servidor     │                          │     Servidor     │
│     (Puerto 55555)                         │     (Puerto 55555)│
│                  │                          │                  │
│  2. Enviar       │ ───────────────────────► │  3. Recibir      │
│     mensaje      │      Mensaje Cifrado     │     y Descifrar  │
│     a 192.168.1.100                        │                  │
└──────────────────┘                          └──────────────────┘
```

### Paso a Paso

#### En AMBAS computadoras:

1. **Iniciar el servidor:**
   - Ve a la pestaña **🌐 Red**
   - Verifica tu IP local (ej: `192.168.1.50`)
   - Haz clic en **▶️ Iniciar Servidor**
   - El estado cambiará a `✅ Escuchando en puerto 55555`

2. **Cargar tu usuario:**
   - Ve a **👤 Usuarios**
   - Carga tu usuario (ej: `alice` o `bob`)

#### Para enviar un mensaje:

1. **En la PC de Alice:**
   - Ve a **🌐 Red**
   - IP del destinatario: `192.168.1.100` (IP de Bob)
   - Nombre: `bob` (para usar su clave pública)
   - Clic en **📡 Enviar Mensaje**
   - Escribe el mensaje y envía

2. **En la PC de Bob:**
   - El mensaje aparece automáticamente en **📨 Historial**
   - Se descifra automáticamente con tu clave privada
   - Recibes una notificación

### 🔑 Intercambiar Claves Públicas

**Opción 1: Manual (Recomendada)**

1. Alice exporta su clave pública (pestaña **🔑 Claves** → **👁️ Ver**)
2. La envía a Bob por email/WhatsApp
3. Bob la importa (pestaña **🔑 Claves** → pegar clave → **💾 Importar**)
4. Bob hace lo mismo y envía su clave a Alice

**Opción 2: Automática por Red**

1. Ambos inician el servidor
2. Cuando Alice envía un mensaje a Bob, puede incluir su clave pública
3. La aplicación de Bob la guarda automáticamente

---

## 📁 Estructura del Proyecto

```
AppMensajeria/
├── main.py                     # Punto de entrada (GUI)
├── main_console.py             # Versión consola (alternativa)
├── gui.py                      # Interfaz gráfica principal
├── network.py                  # Módulo de comunicación LAN ⭐ NUEVO
├── keys.py                     # Gestión de claves RSA
├── crypto.py                   # Cifrado/Descifrado
├── importar_clave_desde_archivo.py
├── requirements.txt            # Dependencias
├── README.md                   # Este archivo
├── claves/                     # Almacén de claves
│   ├── alice_privada.pem
│   ├── alice_publica.pem
│   └── 192.168.1.100_publica.pem  # Claves por IP
└── mensajes/                   # Mensajes cifrados
    └── *.txt
```

---

## 🔑 Importar Clave del Profesor

Si tu profesor te dio un archivo `private-key.pem`:

### Opción 1: Copiar manualmente

1. Copia el archivo a la carpeta `claves`:
   ```bash
   copy private-key.pem claves\profesor_privada.pem
   ```

2. Ejecuta la aplicación
3. Pestaña **👤 Usuarios** → **Cargar Usuario Existente**
4. Nombre: `profesor`
5. Contraseña: (dejar vacío si no tiene)

### Opción 2: Usar script de importación

```bash
python importar_clave_desde_archivo.py private-key.pem
```

---

## 🛠️ Solución de Problemas

### Error: "No se pudo conectar a la IP"

**Causas posibles:**
- La otra PC no tiene el servidor iniciado
- Firewall bloquea el puerto 55555
- Las PCs no están en la misma red

**Solución:**
1. Verifica que AMBAS PCs tengan el servidor iniciado
2. Abre el puerto 55555 en el firewall de Windows
3. Verifica que las IPs sean correctas (misma red: `192.168.1.XXX`)

### Error: "No hay clave pública para el destinatario"

**Solución:**
1. Importa la clave pública del contacto (pestaña **🔑 Claves**)
2. O usa el nombre exacto con el que se guardó la clave

### El servidor no inicia (Puerto en uso)

**Solución:**
1. Cambia el puerto (ej: `55556`)
2. O cierra otras aplicaciones que usen ese puerto

### Firewall de Windows

Para abrir el puerto en el firewall:

```bash
# PowerShell como Administrador
New-NetFirewallRule -DisplayName "Mensajeria RSA" -Direction Inbound -LocalPort 55555 -Protocol TCP -Action Allow
```

---

## ⚠️ Seguridad

- ✅ RSA-OAEP con SHA-256 (estándar seguro)
- ✅ Claves mínimas de 2048 bits
- ✅ Opción de contraseña para clave privada
- ⚠️ **NUNCA compartas tu clave privada**
- ⚠️ La comunicación LAN no está autenticada (solo para redes confiables)
- ⚠️ Límite de ~190 bytes por mensaje (RSA-2048)

---

## 📝 Comandos Útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar GUI (por defecto)
python main.py

# Ejecutar versión consola
python main.py --consola

# Importar clave del profesor
python importar_clave_desde_archivo.py private-key.pem
```

---

## 🎯 Ejemplo Completo: Alice y Bob

### Preparación

**En PC de Alice:**
1. `python main.py`
2. Crear usuario `alice`
3. Ir a **🌐 Red**, anotar IP: `192.168.1.50`
4. Iniciar servidor

**En PC de Bob:**
1. `python main.py`
2. Crear usuario `bob`
3. Ir a **🌐 Red**, anotar IP: `192.168.1.100`
4. Iniciar servidor

### Intercambio de Claves

1. Alice copia su clave pública y se la envía a Bob (WhatsApp/email)
2. Bob importa la clave de Alice (nombre: `alice`)
3. Bob copia su clave pública y se la envía a Alice
4. Alice importa la clave de Bob (nombre: `bob`)

### Enviar Mensaje

**Alice → Bob:**
1. Alice va a **🌐 Red**
2. IP: `192.168.1.100`, Nombre: `bob`
3. Clic en **📡 Enviar Mensaje**
4. Escribe: "Hola Bob, ¿probando la app?"
5. Enviar

**Bob recibe:**
1. Notificación emergente
2. Mensaje en historial: "Hola Bob, ¿probando la app?"
3. Responde siguiendo el mismo proceso

---

**Hecho con ❤️ para la clase de Ciberseguridad**
