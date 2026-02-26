# 📱 Guía Rápida - Aplicación de Mensajería Segura

## 🚀 Inicio Rápido (3 pasos)

### Paso 1: Iniciar la Aplicación
```bash
python main.py
```

### Paso 2: Crear o Cargar Usuario
- **Primera vez**: Ve a "👤 Usuarios" → Crea un nuevo usuario
- **Ya tienes usuario**: Ve a "👤 Usuarios" → Carga tu usuario

### Paso 3: ¡Listo para usar!
Después de cargar tu usuario, la aplicación te preguntará si quieres iniciar el servidor para recibir mensajes.

---

## 📖 ¿Cómo usar cada pestaña?

### 👤 Usuarios
**¿Para qué?** Crear tu identidad y cargar tus claves

**Primer uso:**
1. Escribe tu nombre (ej: "alice")
2. Contraseña opcional (recomendada)
3. Click en "Crear y Generar Claves"
4. ¡Listo! Se crean automáticamente tus claves

**Si ya tienes usuario:**
1. Escribe tu nombre de usuario
2. Contraseña (si la configuraste)
3. Click en "Cargar Usuario"
4. La app te preguntará si quieres iniciar el servidor

---

### 💬 Mensajes
**¿Para qué?** Cifrar mensajes para copiar y pegar (WhatsApp, email, etc.)

**Para cifrar y enviar por chat:**
1. Selecciona un destinatario (debe estar en tus contactos)
2. Escribe tu mensaje
3. Click en "Cifrar y Copiar"
4. El mensaje cifrado se copia al portapapeles
5. Pégalo en WhatsApp, email, o donde quieras

**Para descifrar un mensaje recibido:**
1. Copia el mensaje cifrado que recibiste
2. Pégalo en el campo "Mensaje cifrado"
3. Click en "Descifrar Mensaje"
4. ¡Verás el mensaje original!

---

### 🔑 Claves
**¿Para qué?** Gestionar claves públicas (tuya y de tus contactos)

**Compartir tu clave pública:**
1. Click en "Mostrar" → Aparece tu clave pública
2. Click en "Copiar" → Se copia al portapapeles
3. Envíala por WhatsApp/email a tu contacto

**Agregar un contacto:**
1. Pídele a tu contacto que te envíe su clave pública
2. Escribe el nombre del contacto (ej: "bob")
3. Pega su clave pública en el cuadro
4. Click en "Importar y Guardar"
5. ¡Ya puedes enviarle mensajes cifrados!

---

### 🌐 Red
**¿Para qué?** Enviar mensajes directamente por red local (sin WhatsApp/email)

**Requisito:** Ambas PCs deben estar en la misma red WiFi/Ethernet

**Preparación (hacer una vez):**
1. Anota tu IP (aparece arriba)
2. Click en "Iniciar Servidor"
3. Comparte tu IP con tu contacto

**Enviar mensaje por red:**
1. Pide a tu contacto su IP
2. Asegúrate de tener su clave pública importada (pestaña Claves)
3. Escribe la IP del destinatario
4. Escribe el nombre del contacto
5. Click en "Enviar Mensaje"
6. Escribe el mensaje y envía
7. ¡Tu contacto lo recibe automáticamente!

**Recibir mensajes:**
- Los mensajes aparecen automáticamente en "Mensajes Recibidos"
- También recibes una notificación emergente

---

## ❓ Preguntas Frecuentes

### ¿Cuál es la diferencia entre "Mensajes" y "Red"?

- **Pestaña Mensajes**: Cifra y copia al portapapeles. Lo pegas manualmente en WhatsApp/email/etc.
- **Pestaña Red**: Envía directamente por red local a otra PC con la app

### ¿Necesito la clave pública de mi contacto?

**SÍ, siempre** (para ambos métodos). Sin ella no puedes cifrar mensajes para esa persona.

### ¿Cómo intercambiar claves con un amigo?

1. Ambos van a "🔑 Claves" → "Mostrar" → "Copiar"
2. Se envían sus claves públicas por WhatsApp/email
3. Cada uno va a "Importar clave de contacto"
4. Pegan la clave del otro y guardan
5. ¡Ya pueden enviarse mensajes cifrados!

### Mi firewall bloquea el servidor

**Windows:**
```bash
# PowerShell como Administrador
New-NetFirewallRule -DisplayName "Mensajeria RSA" -Direction Inbound -LocalPort 55555 -Protocol TCP -Action Allow
```

### No puedo enviar por red

**Verifica:**
1. ✅ Ambas PCs tienen el servidor iniciado
2. ✅ Están en la misma red WiFi/Ethernet
3. ✅ Tienes la clave pública del destinatario importada
4. ✅ La IP es correcta
5. ✅ El firewall permite el puerto 55555

---

## 🎯 Ejemplo Completo: Alice y Bob

### Preparación (una sola vez)

**Alice:**
1. Crea usuario "alice"
2. Inicia servidor (anota su IP: `192.168.1.50`)
3. Va a Claves → Copia su clave pública
4. Envía su clave pública a Bob por WhatsApp

**Bob:**
1. Crea usuario "bob"
2. Inicia servidor (anota su IP: `192.168.1.100`)
3. Va a Claves → Importa clave de "alice" (pega lo que Alice le envió)
4. Va a Claves → Copia su clave pública
5. Envía su clave pública a Alice por WhatsApp

**Alice:**
1. Va a Claves → Importa clave de "bob"

### Ahora pueden comunicarse

**Opción 1: Por WhatsApp (portapapeles)**
1. Alice va a 💬 Mensajes
2. Selecciona "bob"
3. Escribe "Hola Bob!"
4. Click "Cifrar y Copiar"
5. Pega en WhatsApp y envía a Bob
6. Bob copia el mensaje cifrado
7. Bob va a 💬 Mensajes → Descifrar
8. Pega el mensaje y descifra

**Opción 2: Por Red Local (directo)**
1. Alice va a 🌐 Red
2. IP: `192.168.1.100` (IP de Bob)
3. Contacto: "bob"
4. Click "Enviar Mensaje"
5. Escribe "Hola Bob!"
6. Envía
7. Bob recibe una notificación automática

---

## 💡 Consejos

✅ **Inicia el servidor si quieres recibir mensajes por red**
✅ **Guarda bien tu contraseña** (no se puede recuperar)
✅ **Nunca compartas tu clave privada** (solo la pública)
✅ **Los mensajes tienen límite de ~190 caracteres** (limitación RSA-2048)

---

## 🆘 Ayuda Adicional

- README completo: `README.md`
- Reportar problemas: https://github.com/anthropics/claude-code/issues
