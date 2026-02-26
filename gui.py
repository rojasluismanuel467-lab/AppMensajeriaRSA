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
        self.interfaces_dict = {}  # Diccionario para mapear opciones de interfaz a info completa

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
        # Frame principal scrollable
        main_frame = ctk.CTkScrollableFrame(self.tab_usuarios, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Información de ayuda
        info_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#2d4a2c")
        info_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            info_frame,
            text="💡 Primer Paso: Carga o Crea tu Usuario",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ade80"
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            info_frame,
            text="• Si es tu primera vez: Crea un nuevo usuario\n"
                 "• Si ya tienes usuario: Carga tu usuario existente\n"
                 "• Si el profesor te dio una clave: Copia el archivo a la carpeta 'claves' y carga ese usuario",
            font=ctk.CTkFont(size=11),
            text_color="#d0d0d0",
            justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # Sección de crear usuario
        crear_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        crear_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        crear_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            crear_frame,
            text="✨ Crear Nuevo Usuario",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")

        ctk.CTkLabel(
            crear_frame,
            text="Se generarán automáticamente tus claves RSA",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")

        ctk.CTkLabel(crear_frame, text="Tu nombre:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_nombre_usuario = ctk.CTkEntry(crear_frame, placeholder_text="Ej: alice, bob, tunombre...")
        self.entry_nombre_usuario.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(crear_frame, text="Contraseña (opcional):").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.entry_contrasena = ctk.CTkEntry(crear_frame, placeholder_text="Para proteger tu clave privada", show="*")
        self.entry_contrasena.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        btn_crear = ctk.CTkButton(
            crear_frame,
            text="✨ Crear y Generar Claves",
            command=self.generar_usuario,
            height=40,
            corner_radius=8,
            fg_color="#10b981"
        )
        btn_crear.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

        # Sección de cargar usuario
        cargar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        cargar_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        cargar_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cargar_frame,
            text="📂 Cargar Usuario Existente",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")

        ctk.CTkLabel(
            cargar_frame,
            text="Si ya creaste un usuario antes, cárgalo aquí",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")

        ctk.CTkLabel(cargar_frame, text="Nombre de usuario:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_nombre_cargar = ctk.CTkEntry(cargar_frame, placeholder_text="Ej: profesor, alice...")
        self.entry_nombre_cargar.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(cargar_frame, text="Contraseña:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.entry_contrasena_cargar = ctk.CTkEntry(cargar_frame, placeholder_text="Solo si la protegiste con contraseña", show="*")
        self.entry_contrasena_cargar.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        btn_cargar = ctk.CTkButton(
            cargar_frame,
            text="🔓 Cargar Usuario",
            command=self.cargar_usuario,
            height=40,
            corner_radius=8,
            fg_color="#4169e1"
        )
        btn_cargar.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

        # Botón cerrar sesión
        btn_cerrar = ctk.CTkButton(
            main_frame,
            text="🚪 Cerrar Sesión",
            command=self.cerrar_sesion,
            height=35,
            corner_radius=8,
            fg_color="#4a4a4a"
        )
        btn_cerrar.grid(row=3, column=0, pady=20)
    
    def crear_tab_mensajes(self):
        """Crea la pestaña de mensajería."""
        self.tab_mensajes.grid_columnconfigure(0, weight=1)
        self.tab_mensajes.grid_rowconfigure(0, weight=1)
        # Frame principal scrollable
        main_frame = ctk.CTkScrollableFrame(self.tab_mensajes, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Información de ayuda
        info_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#1a4d2e")
        info_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            info_frame,
            text="💡 Información",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ade80"
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            info_frame,
            text="Esta pestaña es para cifrar mensajes y copiarlos al portapapeles.\n"
                 "Para enviar directamente por red local, usa la pestaña '🌐 Red'.",
            font=ctk.CTkFont(size=11),
            text_color="#d0d0d0",
            justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # Frame de enviar mensaje
        enviar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        enviar_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        enviar_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            enviar_frame,
            text="📤 Cifrar Mensaje (Portapapeles)",
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
            text="🔒 Cifrar y Copiar",
            command=self.enviar_mensaje,
            height=40,
            corner_radius=8,
            fg_color="#10b981"
        )
        btn_enviar.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

        # Frame de recibir mensaje
        recibir_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        recibir_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        recibir_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            recibir_frame,
            text="📥 Descifrar Mensaje Recibido",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        ctk.CTkLabel(
            recibir_frame,
            text="Pega aquí el mensaje cifrado que recibiste:",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        self.entry_mensaje_cifrado = ctk.CTkTextbox(recibir_frame, height=100, corner_radius=8)
        self.entry_mensaje_cifrado.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        btn_descifrar = ctk.CTkButton(
            recibir_frame,
            text="🔓 Descifrar Mensaje",
            command=self.descifrar_mensaje,
            height=40,
            corner_radius=8,
            fg_color="#f59e0b"
        )
        btn_descifrar.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")

        # Área de resultado
        resultado_frame = ctk.CTkFrame(recibir_frame, corner_radius=8, fg_color="#2a2a2a")
        resultado_frame.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")

        ctk.CTkLabel(
            resultado_frame,
            text="Mensaje descifrado:",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.label_resultado = ctk.CTkLabel(
            resultado_frame,
            text="(aquí aparecerá el mensaje descifrado)",
            font=ctk.CTkFont(size=12),
            text_color="#4ade80",
            justify="left",
            wraplength=800
        )
        self.label_resultado.pack(anchor="w", padx=10, pady=(0, 10))
    
    def crear_tab_claves(self):
        """Crea la pestaña de gestión de claves."""
        self.tab_claves.grid_columnconfigure(0, weight=1)
        # Frame principal scrollable
        main_frame = ctk.CTkScrollableFrame(self.tab_claves, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Información de ayuda
        info_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#2d1b3d")
        info_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            info_frame,
            text="💡 Sobre las Claves",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#b794f4"
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            info_frame,
            text="• Tu clave pública: Compártela con tus contactos para que te envíen mensajes\n"
                 "• Clave de contacto: Importa su clave pública para poder enviarles mensajes cifrados",
            font=ctk.CTkFont(size=11),
            text_color="#d0d0d0",
            justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # Ver clave pública
        public_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        public_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        public_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            public_frame,
            text="📋 Mi Clave Pública",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        ctk.CTkLabel(
            public_frame,
            text="Comparte esta clave con tus contactos:",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.text_clave_publica = ctk.CTkTextbox(public_frame, height=120, corner_radius=8, font=("Consolas", 9))
        self.text_clave_publica.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        btn_frame = ctk.CTkFrame(public_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")

        ctk.CTkButton(
            btn_frame,
            text="👁️ Mostrar",
            command=self.ver_clave_publica,
            width=120,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📋 Copiar",
            command=self.copiar_clave_publica,
            width=120,
            height=35,
            fg_color="#4a4a4a"
        ).pack(side="left", padx=5)

        # Importar clave pública
        importar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        importar_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        importar_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            importar_frame,
            text="📥 Importar Clave de Contacto",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        ctk.CTkLabel(
            importar_frame,
            text="Pega aquí la clave pública que te envió tu contacto:",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        ctk.CTkLabel(importar_frame, text="Nombre del contacto:").grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_nombre_contacto = ctk.CTkEntry(importar_frame, placeholder_text="Ej: bob, alice, profesor...", width=300)
        self.entry_nombre_contacto.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")

        ctk.CTkLabel(importar_frame, text="Clave pública (formato PEM):").grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")
        self.text_importar_clave = ctk.CTkTextbox(importar_frame, height=120, corner_radius=8, font=("Consolas", 9))
        self.text_importar_clave.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            importar_frame,
            text="💾 Importar y Guardar",
            command=self.importar_clave_publica,
            height=40,
            corner_radius=8,
            fg_color="#8b5cf6"
        ).grid(row=6, column=0, padx=20, pady=(10, 20), sticky="w")

        # Lista de contactos
        contactos_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        contactos_frame.grid(row=3, column=0, sticky="ew")

        ctk.CTkLabel(
            contactos_frame,
            text="👥 Mis Contactos",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.lista_contactos = ctk.CTkLabel(
            contactos_frame,
            text="Sin contactos importados",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            justify="left"
        )
        self.lista_contactos.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

    def crear_tab_red(self):
        """Crea la pestaña de configuración de red."""
        self.tab_red.grid_columnconfigure(0, weight=1)
        self.tab_red.grid_rowconfigure(0, weight=1)
        # Frame principal scrollable
        main_frame = ctk.CTkScrollableFrame(self.tab_red, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Información de ayuda
        info_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#1a3a5c")
        info_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(
            info_frame,
            text="💡 Cómo funciona la Red Local",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4da6ff"
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            info_frame,
            text="1. Inicia el servidor para recibir mensajes\n"
                 "2. Comparte tu IP con tus contactos\n"
                 "3. Para enviar, necesitas la IP del destinatario y su clave pública importada",
            font=ctk.CTkFont(size=11),
            text_color="#d0d0d0",
            justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # Información de IP y servidor
        servidor_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        servidor_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        servidor_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            servidor_frame,
            text="🌐 Mi Información de Red",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        ctk.CTkLabel(servidor_frame, text="Interfaz de red:").grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # ComboBox para seleccionar interfaz de red
        self.combo_interfaces = ctk.CTkComboBox(
            servidor_frame,
            values=["Cargando..."],
            command=self.seleccionar_interfaz,
            width=300
        )
        self.combo_interfaces.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # Botón para refrescar interfaces
        ctk.CTkButton(
            servidor_frame,
            text="🔄 Actualizar",
            command=self.actualizar_interfaces,
            width=100,
            height=28,
            corner_radius=6,
            fg_color="#4a4a4a"
        ).grid(row=1, column=2, padx=(0, 20), pady=10)

        ctk.CTkLabel(servidor_frame, text="IP seleccionada:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.label_mi_ip = ctk.CTkLabel(
            servidor_frame,
            text="Selecciona una interfaz",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ade80"
        )
        self.label_mi_ip.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        # Botón para copiar IP
        ctk.CTkButton(
            servidor_frame,
            text="📋 Copiar",
            command=self.copiar_ip,
            width=100,
            height=25,
            corner_radius=6,
            fg_color="#4a4a4a"
        ).grid(row=2, column=2, padx=(0, 20), pady=10)

        ctk.CTkLabel(servidor_frame, text="Puerto:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.entry_puerto = ctk.CTkEntry(servidor_frame, width=100)
        self.entry_puerto.insert(0, str(PUERTO_DEFAULT))
        self.entry_puerto.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        # Estado del servidor
        ctk.CTkLabel(servidor_frame, text="Estado:").grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.label_estado_servidor = ctk.CTkLabel(
            servidor_frame,
            text="⛔ Servidor detenido",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.label_estado_servidor.grid(row=4, column=1, padx=20, pady=10, sticky="w")

        # Botón del servidor
        self.btn_iniciar_servidor = ctk.CTkButton(
            servidor_frame,
            text="▶️ Iniciar Servidor",
            command=self.toggle_servidor,
            height=40,
            corner_radius=8,
            fg_color="#10b981"
        )
        self.btn_iniciar_servidor.grid(row=5, column=0, columnspan=3, padx=20, pady=20)

        # Enviar mensaje por red
        enviar_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        enviar_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        enviar_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            enviar_frame,
            text="📡 Enviar Mensaje por Red",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        ctk.CTkLabel(
            enviar_frame,
            text="Introduce la IP del destinatario (debe tener el servidor activo):",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")

        ctk.CTkLabel(enviar_frame, text="IP destino:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_ip_destino = ctk.CTkEntry(enviar_frame, placeholder_text="Ej: 192.168.1.100")
        self.entry_ip_destino.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(enviar_frame, text="Contacto:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.entry_nombre_destino = ctk.CTkEntry(enviar_frame, placeholder_text="Nombre del contacto")
        self.entry_nombre_destino.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        btn_enviar = ctk.CTkButton(
            enviar_frame,
            text="📤 Enviar Mensaje",
            command=self.enviar_mensaje_red,
            height=40,
            corner_radius=8,
            fg_color="#4169e1"
        )
        btn_enviar.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

        # Historial de mensajes de red
        historial_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#323232")
        historial_frame.grid(row=3, column=0, sticky="ew")
        historial_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            historial_frame,
            text="📨 Mensajes Recibidos por Red",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.text_historial = ctk.CTkTextbox(historial_frame, height=200, corner_radius=8, font=("Consolas", 11))
        self.text_historial.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.text_historial.configure(state="disabled")

        btn_limpiar = ctk.CTkButton(
            historial_frame,
            text="🗑️ Limpiar Historial",
            command=self.limpiar_historial,
            height=30,
            corner_radius=8,
            fg_color="#4a4a4a"
        )
        btn_limpiar.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        # Actualizar interfaces de red disponibles
        self.actualizar_interfaces()

    def actualizar_ip_local(self):
        """Actualiza la etiqueta con la IP local."""
        ip = gestor.obtener_ip_local()
        self.label_mi_ip.configure(text=ip)

    def actualizar_interfaces(self):
        """Actualiza la lista de interfaces de red disponibles."""
        from network import obtener_todas_las_ips

        interfaces = obtener_todas_las_ips()

        if not interfaces:
            self.combo_interfaces.configure(values=["No hay interfaces disponibles"])
            self.combo_interfaces.set("No hay interfaces disponibles")
            self.label_mi_ip.configure(text="Sin interfaces")
            return

        # Crear lista de opciones con formato: "IP - Descripción (Interfaz)"
        opciones = []
        self.interfaces_dict = {}  # Guardar mapeo IP -> info completa

        for nombre, ip, desc in interfaces:
            opcion = f"{ip} - {desc}"
            opciones.append(opcion)
            self.interfaces_dict[opcion] = (nombre, ip, desc)

        self.combo_interfaces.configure(values=opciones)

        # Seleccionar la primera por defecto
        if opciones:
            self.combo_interfaces.set(opciones[0])
            self.seleccionar_interfaz(opciones[0])

        self.actualizar_status(f"Se encontraron {len(interfaces)} interfaz(ces) de red")

    def seleccionar_interfaz(self, eleccion):
        """Callback cuando se selecciona una interfaz."""
        if eleccion and eleccion in self.interfaces_dict:
            nombre, ip, desc = self.interfaces_dict[eleccion]
            self.label_mi_ip.configure(text=ip)
            self.actualizar_status(f"Interfaz seleccionada: {desc} ({ip})")

    def copiar_ip(self):
        """Copia la IP seleccionada al portapapeles."""
        ip = self.label_mi_ip.cget("text")
        if ip and ip not in ["Selecciona una interfaz", "Sin interfaces"]:
            self.clipboard_clear()
            self.clipboard_append(ip)
            self.actualizar_status(f"IP {ip} copiada al portapapeles")
            messagebox.showinfo("IP Copiada", f"Tu IP {ip} ha sido copiada al portapapeles.\n\nCompártela con tus contactos para que puedan enviarte mensajes.")
        else:
            messagebox.showwarning("Sin IP", "Primero selecciona una interfaz de red")
    
    def configurar_gestor_red(self):
        """Configura el gestor de red con el usuario actual."""
        if self.usuario_actual:
            gestor.configurar(
                self.usuario_actual,
                self.mensaje_recibido_red,
                self.estado_red
            )

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
            if not self.usuario_actual:
                messagebox.showwarning(
                    "Usuario Requerido",
                    "Debes cargar un usuario antes de iniciar el servidor.\n\n"
                    "Ve a la pestaña '👤 Usuarios' y carga o crea un usuario."
                )
                return

            try:
                puerto = int(self.entry_puerto.get())
                self.configurar_gestor_red()
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
            import time
            timestamp = time.strftime("%H:%M:%S")
            self.text_historial.configure(state="normal")
            self.text_historial.insert("end", f"[{timestamp}] 📩 De: {origen}\n{mensaje}\n{'-'*50}\n\n")
            self.text_historial.see("end")
            self.text_historial.configure(state="disabled")

            # Notificación
            self.actualizar_status(f"Mensaje recibido de {origen}")
            messagebox.showinfo("📨 Mensaje Recibido", f"De: {origen}\n\n{mensaje}")
    
    def enviar_mensaje_red(self):
        """Envía un mensaje por red."""
        if not self.usuario_actual:
            messagebox.showwarning(
                "Usuario Requerido",
                "Debes cargar un usuario antes de enviar mensajes.\n\n"
                "Ve a la pestaña '👤 Usuarios' y carga o crea un usuario."
            )
            return

        ip = self.entry_ip_destino.get().strip()
        nombre_destino = self.entry_nombre_destino.get().strip()

        if not ip:
            messagebox.showerror("Error", "Ingresa la IP del destinatario")
            return

        # Verificar que exista la clave pública del destinatario
        if nombre_destino:
            ruta_clave = Path(f"claves/{nombre_destino}_publica.pem")
            if not ruta_clave.exists():
                respuesta = messagebox.askyesno(
                    "Clave Pública No Encontrada",
                    f"No se encontró la clave pública de '{nombre_destino}'.\n\n"
                    f"Para enviar mensajes cifrados necesitas importar su clave pública.\n\n"
                    f"¿Quieres ir a la pestaña de Claves para importarla?"
                )
                if respuesta:
                    self.tabview.set("🔑 Claves")
                return

        # Configurar gestor si no está configurado
        self.configurar_gestor_red()

        # Pedir mensaje
        dialog = ctk.CTkToplevel(self)
        dialog.title("Enviar Mensaje")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"📡 Enviando a: {ip}" + (f" ({nombre_destino})" if nombre_destino else ""),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)

        text_mensaje = ctk.CTkTextbox(dialog, height=150, corner_radius=8)
        text_mensaje.pack(padx=20, pady=10, fill="both", expand=True)
        text_mensaje.focus()

        def enviar():
            mensaje = text_mensaje.get("0.0", "end").strip()
            if not mensaje:
                messagebox.showerror("Error", "El mensaje no puede estar vacío")
                return

            exito = gestor.enviar_a(ip, mensaje, nombre_destino if nombre_destino else None)

            if exito:
                messagebox.showinfo("Éxito", "✅ Mensaje enviado correctamente")
                self.actualizar_status(f"Mensaje enviado a {ip}")
                dialog.destroy()
            else:
                messagebox.showerror(
                    "Error al Enviar",
                    "No se pudo enviar el mensaje.\n\n"
                    "Posibles causas:\n"
                    "• El destinatario no tiene el servidor activo\n"
                    "• La IP es incorrecta\n"
                    "• Hay un firewall bloqueando la conexión\n"
                    "• No existe la clave pública del destinatario"
                )

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="📤 Enviar",
            command=enviar,
            height=35,
            width=150,
            corner_radius=8,
            fg_color="#10b981"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            height=35,
            width=100,
            corner_radius=8,
            fg_color="#4a4a4a"
        ).pack(side="left", padx=5)
    
    def limpiar_historial(self):
        """Limpia el historial de mensajes."""
        self.text_historial.configure(state="normal")
        self.text_historial.delete("0.0", "end")
        self.text_historial.configure(state="disabled")
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
        if hasattr(self, 'status_label'):
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

            # Configurar el gestor de red con el nuevo usuario
            self.configurar_gestor_red()

            self.actualizar_usuario_label()
            self.actualizar_status(f"Usuario '{nombre}' cargado correctamente")

            self.entry_nombre_cargar.delete(0, 'end')
            self.entry_contrasena_cargar.delete(0, 'end')

            # Preguntar si quiere iniciar el servidor
            if not self.servidor_activo:
                respuesta = messagebox.askyesno(
                    "Iniciar Servidor",
                    f"¡Bienvenido {nombre}!\n\n"
                    "¿Quieres iniciar el servidor para recibir mensajes?\n\n"
                    "Puedes hacerlo después desde la pestaña '🌐 Red'"
                )
                if respuesta:
                    self.tabview.set("🌐 Red")
                    # Pequeño delay para que la UI se actualice
                    self.after(100, self.toggle_servidor)
                else:
                    # Cambiar a pestaña de mensajes
                    self.tabview.set("💬 Mensajes")
            else:
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
            messagebox.showwarning(
                "Usuario Requerido",
                "Debes cargar un usuario antes de enviar mensajes.\n\n"
                "Ve a la pestaña '👤 Usuarios' y carga o crea un usuario."
            )
            return

        destinatario = self.combo_destinatario.get()
        if destinatario == "Sin contactos" or not destinatario:
            messagebox.showinfo(
                "Sin Contactos",
                "No hay contactos disponibles.\n\n"
                "Para enviar mensajes, primero debes:\n"
                "1. Ir a la pestaña '🔑 Claves'\n"
                "2. Importar la clave pública de tu contacto"
            )
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
                "✅ Mensaje Cifrado",
                f"Mensaje cifrado correctamente y copiado al portapapeles.\n\n"
                f"📋 Ahora puedes pegarlo en WhatsApp, email, etc. y enviarlo a '{destinatario}'\n\n"
                f"💡 Tip: Para enviar directamente por red local, usa la pestaña '🌐 Red'"
            )

            self.actualizar_status(f"Mensaje cifrado para '{destinatario}'")
            self.entry_mensaje.delete("0.0", "end")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cifrar: {e}")
            self.actualizar_status(f"Error: {e}", es_error=True)
    
    def descifrar_mensaje(self):
        """Descifra un mensaje recibido."""
        if not self.usuario_actual:
            messagebox.showwarning(
                "Usuario Requerido",
                "Debes cargar un usuario antes de descifrar mensajes.\n\n"
                "Ve a la pestaña '👤 Usuarios' y carga o crea un usuario."
            )
            return

        mensaje_cifrado = self.entry_mensaje_cifrado.get("0.0", "end").strip()
        if not mensaje_cifrado:
            messagebox.showerror("Error", "Debes pegar el mensaje cifrado primero")
            return

        try:
            mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, self.usuario_actual["clave_privada"])

            self.label_resultado.configure(text=f"{mensaje_descifrado}")

            # Guardar mensaje
            Path("mensajes").mkdir(exist_ok=True)
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"recibido_por_{self.usuario_actual['nombre']}_{timestamp}.txt"
            ruta_guardado = f"mensajes/{nombre_archivo}"
            Path(ruta_guardado).write_text(mensaje_descifrado, encoding='utf-8')

            messagebox.showinfo(
                "✅ Mensaje Descifrado",
                f"Mensaje descifrado correctamente.\n\n"
                f"📄 Guardado en: {ruta_guardado}"
            )
            self.actualizar_status("Mensaje descifrado correctamente")

        except Exception as e:
            messagebox.showerror(
                "Error al Descifrar",
                f"No se pudo descifrar el mensaje.\n\n"
                f"Posibles causas:\n"
                f"• El mensaje no fue cifrado con tu clave pública\n"
                f"• El mensaje está corrupto o incompleto\n"
                f"• No es un mensaje válido en formato Base64\n\n"
                f"Error técnico: {e}"
            )
            self.actualizar_status("Error al descifrar", es_error=True)


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
