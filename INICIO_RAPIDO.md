# 🚀 Inicio Rápido

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python main.py
```

¡Eso es todo! La aplicación se abrirá automáticamente.

---

## ✅ Cambios Implementados

### 1. Detección de IP Mejorada
- ✅ Lista TODAS las interfaces de red disponibles
- ✅ Detecta automáticamente ZeroTier, WiFi, Ethernet, VMs
- ✅ Selector visual para elegir la interfaz a usar
- ✅ Botón "Actualizar IPs" para refrescar la lista

### 2. UI Moderna con Flet
- ✅ Diseño Material Design (Flutter)
- ✅ Mucho más intuitiva y fácil de usar
- ✅ Flujo de trabajo claro
- ✅ Animaciones suaves
- ✅ Responsive

---

## 🎯 Primer Uso

1. **Ejecuta**: `python main.py`
2. **Pestaña Inicio**: Crea tu usuario
3. **Pestaña Red**:
   - Click "Actualizar IPs"
   - Selecciona tu interfaz (WiFi, ZeroTier, etc.)
   - Click "Iniciar Servidor"
4. **Pestaña Contactos**: Importa claves de tus contactos
5. ¡Listo para enviar mensajes!

---

## 📱 Uso con ZeroTier

Si usas ZeroTier para conectarte con amigos fuera de tu red local:

1. Conéctate a tu red ZeroTier
2. Abre la app: `python main.py`
3. Ve a "🌐 Red"
4. Click "Actualizar IPs"
5. Selecciona la interfaz que dice "ZeroTier (VPN)"
6. Inicia el servidor
7. Comparte esa IP con tus contactos

---

## 🔧 Backend Verificado

Todo el backend ha sido probado y funciona correctamente:

- ✅ Generación de claves RSA
- ✅ Cifrado/descifrado de mensajes
- ✅ Gestión de contactos
- ✅ Servidor de red
- ✅ Envío de mensajes por red
- ✅ Detección de múltiples interfaces
- ✅ Compatibilidad con ZeroTier

---

## 📋 Dependencias

- **flet**: UI moderna (Material Design)
- **cryptography**: Cifrado RSA
- **netifaces**: Detección de interfaces de red

Todas se instalan con:
```bash
pip install -r requirements.txt
```

---

## 💡 Tips

- La app ahora SOLO usa la nueva UI (más simple)
- Si tienes problemas con una interfaz, usa "Actualizar IPs"
- ZeroTier aparece claramente marcado como "(VPN)"
- El servidor debe estar activo en AMBAS PCs para enviar/recibir

---

**¡Disfruta de tu app de mensajería segura! 🔐**
