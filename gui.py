"""
Interfaz gráfica para la Aplicación de Mensajería Segura con RSA.
Usa customtkinter para un diseño moderno y minimalista.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import os

from keys import (
    generar_par_claves,
    guardar_clave_privada,
    guardar_clave_publica,
    cargar_clave_privada,
    cargar_clave_publica,
    obtener_clave_publica_desde_privada,
    exportar_clave_publica_pem,
    importar_clave_publica_pem,
)
from crypto import cifrar_mensaje, descifrar_mensaje
from network import gestor, PUERTO_DEFAULT


# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MensajeApp(ctk.CTk):
    """Aplicación principal de mensajería segura."""

    def __init__(self):
        super().__init__()

        self.usuario_actual = None
        self.contactos = []
        self.servidor_activo = False

        # Configurar ventana principal
        self.title("🔐 Mensajería Segura RSA")
        self.geometry("1000x700")
        self.minsize(900, 650)

        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Crear contenedor principal con sombra simulada
        self.container = ctk.CTkFrame(self, corner_radius=15, fg_color="#2b2b2b")
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        # Crear header
        self.crear_header()

        # Crear contenido principal
        self.crear_contenido()

        # Crear barra de estado
        self.crear_status_bar()
    
    def crear_header(self):
        """Crea el encabezado de la aplicación."""
        header = ctk.CTkFrame(self.container, height=80, corner_radius=15, fg_color="#1a1a2e")
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header.grid_columnconfigure(0, weight=1)
        
        # Título
        titulo_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_frame.grid(row=0, column=0, padx=30, pady=15, sticky="w")
        
        titulo = ctk.CTkLabel(
            titulo_frame,
            text="🔐 Mensajería Segura",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            titulo_frame,
            text="Cifrado RSA con OAEP-SHA256",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle.pack(anchor="w")
        
        # Info del usuario
        self.usuario_label = ctk.CTkLabel(
            header,
            text="👤 Sin usuario",
            font=ctk.CTkFont(size=14),
            text_color="#4ade80"
        )
        self.usuario_label.grid(row=0, column=1, padx=30, pady=20, sticky="e")
    
    def crear_contenido(self):
        """Crea el contenido principal con pestañas."""
        # Contenedor de pestañas
        self.tabview = ctk.CTkTabview(self.container, corner_radius=10, fg_color="#2b2b2b")
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.tabview.grid_columnconfigure(0, weight=1)
        self.tabview.grid_rowconfigure(0, weight=1)

        # Crear pestañas
        self.tab_usuarios = self.tabview.add("👤 Usuarios")
        self.tab_mensajes = self.tabview.add("💬 Mensajes")
        self.tab_claves = self.tabview.add("🔑 Claves")
        self.tab_red = self.tabview.add("🌐 Red")

        # Configurar cada pestaña
        self.crear_tab_usuarios()
        self.crear_tab_mensajes()
        self.crear_tab_claves()
        self.crear_tab_red()
    
    def crear_tab_usuarios(self):
        """Crea la pestaña de gestión de usuarios."""
        self.tab_usuarios.grid_columnconfigure(0, weight=1)
        
        # Frame principal con padding
        main_frame = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Sección de crear usuario
        crear_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        crear_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        crear_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            crear_frame,
            text="Crear Nuevo Usuario",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(crear_frame, text="Nombre:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.entry_nombre_usuario = ctk.CTkEntry(crear_frame, placeholder_text="Ej: alice")
        self.entry_nombre_usuario.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(crear_frame, text="Contraseña (opcional):").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_contrasena = ctk.CTkEntry(crear_frame, placeholder_text="Proteger clave privada", show="*")
        self.entry_contrasena.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        btn_crear = ctk.CTkButton(
            crear_frame,
            text="✨ Generar Claves",
            command=self.generar_usuario,
            height=40,
            corner_radius=8
        )
        btn_crear.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        # Sección de cargar usuario
        cargar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        cargar_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        cargar_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            cargar_frame,
            text="Cargar Usuario Existente",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(cargar_frame, text="Nombre:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.entry_nombre_cargar = ctk.CTkEntry(cargar_frame, placeholder_text="Ej: profesor")
        self.entry_nombre_cargar.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(cargar_frame, text="Contraseña:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_contrasena_cargar = ctk.CTkEntry(cargar_frame, placeholder_text="Si tiene contraseña", show="*")
        self.entry_contrasena_cargar.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        btn_cargar = ctk.CTkButton(
            cargar_frame,
            text="📂 Cargar Usuario",
            command=self.cargar_usuario,
            height=40,
            corner_radius=8,
            fg_color="#4169e1"
        )
        btn_cargar.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        # Botón cerrar sesión
        btn_cerrar = ctk.CTkButton(
            main_frame,
            text="🚪 Cerrar Sesión",
            command=self.cerrar_sesion,
            height=40,
            corner_radius=8,
            fg_color="#4a4a4a"
        )
        btn_cerrar.grid(row=2, column=0, pady=20)
    
    def crear_tab_mensajes(self):
        """Crea la pestaña de mensajería."""
        self.tab_mensajes.grid_columnconfigure(0, weight=1)
        self.tab_mensajes.grid_rowconfigure(1, weight=1)
        
        main_frame = ctk.CTkFrame(self.tab_mensajes, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Frame de enviar mensaje
        enviar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        enviar_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        enviar_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            enviar_frame,
            text="📤 Enviar Mensaje Cifrado",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(enviar_frame, text="Destinatario:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.combo_destinatario = ctk.CTkComboBox(enviar_frame, values=["Sin contactos"])
        self.combo_destinatario.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(enviar_frame, text="Mensaje:").grid(row=2, column=0, padx=20, pady=10, sticky="nw")
        self.entry_mensaje = ctk.CTkTextbox(enviar_frame, height=100, corner_radius=8)
        self.entry_mensaje.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        btn_enviar = ctk.CTkButton(
            enviar_frame,
            text="🔒 Cifrar y Enviar",
            command=self.enviar_mensaje,
            height=40,
            corner_radius=8,
            fg_color="#10b981"
        )
        btn_enviar.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        # Frame de recibir mensaje
        recibir_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        recibir_frame.grid(row=1, column=0, pady=(0, 20), sticky="nsew")
        recibir_frame.grid_columnconfigure(0, weight=1)
        recibir_frame.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(
            recibir_frame,
            text="📥 Recibir Mensaje",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(recibir_frame, text="Mensaje cifrado (Base64):").grid(row=1, column=0, padx=20, pady=10, sticky="nw")
        self.entry_mensaje_cifrado = ctk.CTkTextbox(recibir_frame, height=80, corner_radius=8)
        self.entry_mensaje_cifrado.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        btn_descifrar = ctk.CTkButton(
            recibir_frame,
            text="🔓 Descifrar Mensaje",
            command=self.descifrar_mensaje,
            height=40,
            corner_radius=8,
            fg_color="#f59e0b"
        )
        btn_descifrar.grid(row=2, column=0, padx=20, pady=20, sticky="w")
        
        # Área de resultado
        self.label_resultado = ctk.CTkLabel(
            recibir_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#4ade80",
            justify="left"
        )
        self.label_resultado.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")
    
    def crear_tab_claves(self):
        """Crea la pestaña de gestión de claves."""
        self.tab_claves.grid_columnconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self.tab_claves, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Ver clave pública
        public_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        public_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        public_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            public_frame,
            text="📋 Mi Clave Pública",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.text_clave_publica = ctk.CTkTextbox(public_frame, height=150, corner_radius=8, font=("Consolas", 10))
        self.text_clave_publica.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        btn_frame = ctk.CTkFrame(public_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        ctk.CTkButton(
            btn_frame,
            text="👁️ Ver Clave",
            command=self.ver_clave_publica,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📋 Copiar",
            command=self.copiar_clave_publica,
            width=120,
            fg_color="#4a4a4a"
        ).pack(side="left", padx=5)
        
        # Importar clave pública
        importar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        importar_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        importar_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            importar_frame,
            text="📥 Importar Clave Pública de Contacto",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(importar_frame, text="Nombre del contacto:").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.entry_nombre_contacto = ctk.CTkEntry(importar_frame, placeholder_text="Ej: bob", width=200)
        self.entry_nombre_contacto.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        ctk.CTkLabel(importar_frame, text="Clave pública PEM:").grid(row=2, column=0, padx=20, pady=(15, 5), sticky="w")
        self.text_importar_clave = ctk.CTkTextbox(importar_frame, height=120, corner_radius=8, font=("Consolas", 10))
        self.text_importar_clave.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkButton(
            importar_frame,
            text="💾 Importar Clave",
            command=self.importar_clave_publica,
            height=35,
            corner_radius=8,
            fg_color="#8b5cf6"
        ).grid(row=4, column=0, padx=20, pady=20, sticky="w")
        
        # Lista de contactos
        contactos_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        contactos_frame.grid(row=2, column=0, sticky="ew")
        
        ctk.CTkLabel(
            contactos_frame,
            text="👥 Contactos Disponibles",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.lista_contactos = ctk.CTkLabel(
            contactos_frame,
            text="Sin contactos",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.lista_contactos.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

    def crear_tab_red(self):
        """Crea la pestaña de configuración de red."""
        self.tab_red.grid_columnconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self.tab_red, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Información de IP
        ip_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        ip_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        ip_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            ip_frame,
            text="🌐 Configuración de Red LAN",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(ip_frame, text="Tu IP local:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.label_mi_ip = ctk.CTkLabel(
            ip_frame,
            text="Calculando...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ade80"
        )
        self.label_mi_ip.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(ip_frame, text="Puerto:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_puerto = ctk.CTkEntry(ip_frame, width=100)
        self.entry_puerto.insert(0, str(PUERTO_DEFAULT))
        self.entry_puerto.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Botones del servidor
        btn_frame_servidor = ctk.CTkFrame(ip_frame, fg_color="transparent")
        btn_frame_servidor.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        
        self.btn_iniciar_servidor = ctk.CTkButton(
            btn_frame_servidor,
            text="▶️ Iniciar Servidor",
            command=self.toggle_servidor,
            height=35,
            corner_radius=8,
            fg_color="#10b981"
        )
        self.btn_iniciar_servidor.pack(side="left", padx=5)
        
        self.label_estado_servidor = ctk.CTkLabel(
            btn_frame_servidor,
            text="⛔ Servidor detenido",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.label_estado_servidor.pack(side="left", padx=20)
        
        # Conectar a otro usuario
        conectar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        conectar_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        conectar_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            conectar_frame,
            text="🔗 Conectar a Otro Usuario",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(conectar_frame, text="IP del destinatario:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.entry_ip_destino = ctk.CTkEntry(conectar_frame, placeholder_text="Ej: 192.168.1.100", width=200)
        self.entry_ip_destino.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(conectar_frame, text="Nombre (para clave):").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_nombre_destino = ctk.CTkEntry(conectar_frame, placeholder_text="Ej: alice", width=200)
        self.entry_nombre_destino.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        btn_conectar = ctk.CTkButton(
            conectar_frame,
            text="📡 Enviar Mensaje",
            command=self.enviar_mensaje_red,
            height=35,
            corner_radius=8,
            fg_color="#4169e1"
        )
        btn_conectar.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        # Historial de mensajes de red
        historial_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        historial_frame.grid(row=2, column=0, sticky="nsew")
        historial_frame.grid_columnconfigure(0, weight=1)
        historial_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            historial_frame,
            text="📨 Mensajes Recibidos",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.text_historial = ctk.CTkTextbox(historial_frame, height=150, corner_radius=8, font=("Consolas", 11))
        self.text_historial.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        btn_limpiar = ctk.CTkButton(
            historial_frame,
            text="🗑️ Limpiar Historial",
            command=self.limpiar_historial,
            height=30,
            corner_radius=8,
            fg_color="#4a4a4a"
        )
        btn_limpiar.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Actualizar IP local
        self.actualizar_ip_local()

    def actualizar_ip_local(self):
        """Actualiza la etiqueta con la IP local."""
        ip = gestor.obtener_ip_local()
        self.label_mi_ip.configure(text=ip)
    
    def toggle_servidor(self):
        """Inicia o detiene el servidor."""
        if self.servidor_activo:
            gestor.detener_servidor()
            self.servidor_activo = False
            self.btn_iniciar_servidor.configure(
                text="▶️ Iniciar Servidor",
                fg_color="#10b981"
            )
            self.label_estado_servidor.configure(
                text="⛔ Servidor detenido",
                text_color="#888888"
            )
        else:
            try:
                puerto = int(self.entry_puerto.get())
                gestor.configurar(
                    self.usuario_actual if self.usuario_actual else {},
                    self.mensaje_recibido_red,
                    self.estado_red
                )
                gestor.iniciar_servidor(puerto)
                self.servidor_activo = True
                self.btn_iniciar_servidor.configure(
                    text="⏹️ Detener Servidor",
                    fg_color="#ef4444"
                )
                self.label_estado_servidor.configure(
                    text=f"✅ Escuchando en puerto {puerto}",
                    text_color="#4ade80"
                )
                self.actualizar_status(f"Servidor iniciado en puerto {puerto}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo iniciar el servidor: {e}")
    
    def estado_red(self, mensaje: str):
        """Actualiza el estado de red."""
        self.label_estado_servidor.configure(text=mensaje)
        self.actualizar_status(mensaje)
    
    def mensaje_recibido_red(self, data: dict):
        """Maneja mensajes recibidos por red."""
        if data.get('tipo') == 'recibido_cifrado':
            origen = data.get('origen', 'desconocido')
            mensaje = data.get('mensaje_descifrado', '')
            
            # Agregar al historial
            hora = Path("mensajes").stat().st_mtime if Path("mensajes").exists() else 0
            self.text_historial.insert("end", f"📩 De: {origen}\n{mensaje}\n\n")
            self.text_historial.see("end")
            
            # Notificación
            self.actualizar_status(f"Mensaje recibido de {origen}")
            messagebox.showinfo("Mensaje Recibido", f"Mensaje de {origen}:\n\n{mensaje}")
    
    def enviar_mensaje_red(self):
        """Envía un mensaje por red."""
        if not self.usuario_actual:
            messagebox.showwarning("Advertencia", "Debes cargar un usuario primero")
            return
        
        ip = self.entry_ip_destino.get().strip()
        nombre_destino = self.entry_nombre_destino.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Ingresa la IP del destinatario")
            return
        
        # Pedir mensaje
        dialog = ctk.CTkToplevel(self)
        dialog.title("Enviar Mensaje")
        dialog.geometry("500x400")
        dialog.transient(self)
        
        ctk.CTkLabel(
            dialog,
            text=f"Enviando a: {ip}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)
        
        text_mensaje = ctk.CTkTextbox(dialog, height=150, corner_radius=8)
        text_mensaje.pack(padx=20, pady=10, fill="both", expand=True)
        
        def enviar():
            mensaje = text_mensaje.get("0.0", "end").strip()
            if not mensaje:
                messagebox.showerror("Error", "El mensaje no puede estar vacío")
                return
            
            exito = gestor.enviar_a(ip, mensaje, nombre_destino if nombre_destino else None)
            
            if exito:
                messagebox.showinfo("Éxito", "Mensaje enviado correctamente")
                self.actualizar_status(f"Mensaje enviado a {ip}")
            else:
                messagebox.showerror("Error", "No se pudo enviar el mensaje.\nVerifica la IP y que el servidor esté activo.")
            
            dialog.destroy()
        
        ctk.CTkButton(
            dialog,
            text="📤 Enviar",
            command=enviar,
            height=35,
            corner_radius=8
        ).pack(pady=10)
    
    def limpiar_historial(self):
        """Limpia el historial de mensajes."""
        self.text_historial.delete("0.0", "end")
        self.actualizar_status("Historial limpiado")

    def crear_status_bar(self):
        """Crea la barra de estado inferior."""
        status = ctk.CTkFrame(self.container, height=30, fg_color="#1a1a2e")
        status.grid(row=2, column=0, sticky="ew", padx=2, pady=(0, 2))
        
        self.status_label = ctk.CTkLabel(
            status,
            text="✅ Listo",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.status_label.pack(pady=5)
    
    # ==================== MÉTODOS DE FUNCIONALIDAD ====================
    
    def actualizar_status(self, mensaje: str, es_error: bool = False):
        """Actualiza la barra de estado."""
        self.status_label.configure(
            text=f"{'❌' if es_error else '✅'} {mensaje}",
            text_color="#ef4444" if es_error else "#888888"
        )
    
    def actualizar_usuario_label(self):
        """Actualiza la etiqueta del usuario actual."""
        if self.usuario_actual:
            self.usuario_label.configure(text=f"👤 {self.usuario_actual['nombre']}")
            self.actualizar_contactos()
            self.ver_clave_publica()
        else:
            self.usuario_label.configure(text="👤 Sin usuario")
    
    def actualizar_contactos(self):
        """Actualiza la lista de contactos disponibles."""
        contactos = []
        carpeta_claves = Path("claves")
        
        if carpeta_claves.exists():
            for archivo in carpeta_claves.glob("*_publica.pem"):
                nombre = archivo.stem.replace("_publica", "")
                if self.usuario_actual and nombre != self.usuario_actual["nombre"]:
                    contactos.append(nombre)
        
        self.contactos = contactos
        
        if contactos:
            self.combo_destinatario.configure(values=contactos)
            self.lista_contactos.configure(
                text=", ".join(contactos),
                text_color="#4ade80"
            )
        else:
            self.combo_destinatario.configure(values=["Sin contactos"])
            self.lista_contactos.configure(
                text="Sin contactos",
                text_color="#888888"
            )
    
    def generar_usuario(self):
        """Genera un nuevo par de claves para un usuario."""
        nombre = self.entry_nombre_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        try:
            clave_privada, clave_publica = generar_par_claves(2048)
            
            ruta_privada = f"claves/{nombre}_privada.pem"
            ruta_publica = f"claves/{nombre}_publica.pem"
            
            Path("claves").mkdir(exist_ok=True)
            
            guardar_clave_privada(clave_privada, ruta_privada, contrasena if contrasena else None)
            guardar_clave_publica(clave_publica, ruta_publica)
            
            messagebox.showinfo(
                "Éxito",
                f"Claves generadas para '{nombre}'\n\n"
                f"Clave privada: {ruta_privada}\n"
                f"Clave pública: {ruta_publica}"
            )
            
            self.actualizar_status(f"Usuario '{nombre}' creado")
            self.entry_nombre_usuario.delete(0, 'end')
            self.entry_contrasena.delete(0, 'end')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar claves: {e}")
            self.actualizar_status(f"Error: {e}", es_error=True)
    
    def cargar_usuario(self):
        """Carga un usuario existente desde su clave privada."""
        nombre = self.entry_nombre_cargar.get().strip()
        contrasena = self.entry_contrasena_cargar.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        ruta_privada = f"claves/{nombre}_privada.pem"
        
        if not Path(ruta_privada).exists():
            messagebox.showerror("Error", f"No se encontró la clave privada para '{nombre}'")
            self.actualizar_status(f"Clave no encontrada: {nombre}", es_error=True)
            return
        
        try:
            clave_privada = cargar_clave_privada(ruta_privada, contrasena if contrasena else None)
            clave_publica = obtener_clave_publica_desde_privada(clave_privada)
            
            self.usuario_actual = {
                "nombre": nombre,
                "clave_privada": clave_privada,
                "clave_publica": clave_publica,
            }
            
            self.actualizar_usuario_label()
            self.actualizar_status(f"Usuario '{nombre}' cargado")
            
            self.entry_nombre_cargar.delete(0, 'end')
            self.entry_contrasena_cargar.delete(0, 'end')
            
            # Cambiar a pestaña de mensajes
            self.tabview.set("💬 Mensajes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la clave: {e}")
            self.actualizar_status(f"Error: {e}", es_error=True)
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual."""
        self.usuario_actual = None
        self.actualizar_usuario_label()
        self.actualizar_status("Sesión cerrada")
        
        # Limpiar campos
        if hasattr(self, 'text_clave_publica'):
            self.text_clave_publica.delete("0.0", "end")
        if hasattr(self, 'label_resultado'):
            self.label_resultado.configure(text="")
    
    def ver_clave_publica(self):
        """Muestra la clave pública del usuario actual."""
        if not self.usuario_actual:
            messagebox.showwarning("Advertencia", "Debes cargar un usuario primero")
            return
        
        pem_publica = exportar_clave_publica_pem(self.usuario_actual["clave_publica"])
        
        self.text_clave_publica.delete("0.0", "end")
        self.text_clave_publica.insert("0.0", pem_publica)
        self.actualizar_status("Clave pública mostrada")
    
    def copiar_clave_publica(self):
        """Copia la clave pública al portapapeles."""
        if not self.usuario_actual:
            messagebox.showwarning("Advertencia", "Debes cargar un usuario primero")
            return
        
        pem_publica = exportar_clave_publica_pem(self.usuario_actual["clave_publica"])
        self.clipboard_clear()
        self.clipboard_append(pem_publica)
        self.actualizar_status("Clave pública copiada al portapapeles")
    
    def importar_clave_publica(self):
        """Importa la clave pública de un contacto."""
        nombre = self.entry_nombre_contacto.get().strip()
        pem_clave = self.text_importar_clave.get("0.0", "end").strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre del contacto no puede estar vacío")
            return
        
        if not pem_clave:
            messagebox.showerror("Error", "Debes pegar la clave pública PEM")
            return
        
        try:
            clave_publica = importar_clave_publica_pem(pem_clave)
            
            Path("claves").mkdir(exist_ok=True)
            ruta_guardado = f"claves/{nombre}_publica.pem"
            guardar_clave_publica(clave_publica, ruta_guardado)
            
            messagebox.showinfo("Éxito", f"Clave pública de '{nombre}' guardada")
            self.actualizar_status(f"Contacto '{nombre}' agregado")
            
            self.entry_nombre_contacto.delete(0, 'end')
            self.text_importar_clave.delete("0.0", "end")
            
            self.actualizar_contactos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar clave: {e}")
            self.actualizar_status(f"Error: {e}", es_error=True)
    
    def enviar_mensaje(self):
        """Cifra y envía un mensaje a un contacto."""
        if not self.usuario_actual:
            messagebox.showwarning("Advertencia", "Debes cargar un usuario primero")
            return
        
        destinatario = self.combo_destinatario.get()
        if destinatario == "Sin contactos":
            messagebox.showerror("Error", "No hay contactos disponibles")
            return
        
        mensaje = self.entry_mensaje.get("0.0", "end").strip()
        if not mensaje:
            messagebox.showerror("Error", "El mensaje no puede estar vacío")
            return
        
        try:
            # Cargar clave pública del destinatario
            ruta_publica = f"claves/{destinatario}_publica.pem"
            clave_publica_destinatario = cargar_clave_publica(ruta_publica)
            
            # Cifrar mensaje
            mensaje_cifrado = cifrar_mensaje(mensaje, clave_publica_destinatario)
            
            # Guardar mensaje
            Path("mensajes").mkdir(exist_ok=True)
            nombre_archivo = f"{self.usuario_actual['nombre']}_para_{destinatario}.txt"
            ruta_mensaje = f"mensajes/{nombre_archivo}"
            Path(ruta_mensaje).write_text(mensaje_cifrado, encoding='utf-8')
            
            # Copiar al portapapeles
            self.clipboard_clear()
            self.clipboard_append(mensaje_cifrado)
            
            messagebox.showinfo(
                "Mensaje Cifrado",
                f"Mensaje cifrado y copiado al portapapeles.\n\n"
                f"Envía este texto a '{destinatario}'"
            )
            
            self.actualizar_status(f"Mensaje enviado a '{destinatario}'")
            self.entry_mensaje.delete("0.0", "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cifrar: {e}")
            self.actualizar_status(f"Error: {e}", es_error=True)
    
    def descifrar_mensaje(self):
        """Descifra un mensaje recibido."""
        if not self.usuario_actual:
            messagebox.showwarning("Advertencia", "Debes cargar un usuario primero")
            return
        
        mensaje_cifrado = self.entry_mensaje_cifrado.get("0.0", "end").strip()
        if not mensaje_cifrado:
            messagebox.showerror("Error", "El mensaje cifrado no puede estar vacío")
            return
        
        try:
            mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, self.usuario_actual["clave_privada"])
            
            self.label_resultado.configure(text=f"📩 {mensaje_descifrado}")
            
            # Guardar mensaje
            Path("mensajes").mkdir(exist_ok=True)
            nombre_archivo = f"recibido_por_{self.usuario_actual['nombre']}.txt"
            ruta_guardado = f"mensajes/{nombre_archivo}"
            Path(ruta_guardado).write_text(mensaje_descifrado, encoding='utf-8')
            
            messagebox.showinfo("Éxito", "Mensaje descifrado correctamente")
            self.actualizar_status("Mensaje descifrado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al descifrar: {e}\n\nVerifica que el mensaje fue cifrado con tu clave pública.")
            self.actualizar_status(f"Error al descifrar", es_error=True)


def main():
    """Función principal para iniciar la aplicación."""
    # Crear directorios necesarios
    Path("claves").mkdir(exist_ok=True)
    Path("mensajes").mkdir(exist_ok=True)

    # Iniciar aplicación
    app = MensajeApp()
    
    # Configurar cierre limpio
    def on_closing():
        gestor.cerrar()
        app.destroy()
    
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
