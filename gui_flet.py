"""
Interfaz gráfica moderna con Flet para la Aplicación de Mensajería Segura RSA.
UI completamente rediseñada para ser más intuitiva y fácil de usar.
"""

import flet as ft
from pathlib import Path
import time
from typing import Optional

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
from network import gestor, PUERTO_DEFAULT, obtener_todas_las_ips


class MensajeriaApp:
    """Aplicación principal de mensajería segura con Flet."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.usuario_actual = None
        self.servidor_activo = False
        self.ip_seleccionada = None

        # Configurar página
        self.page.title = "🔐 Mensajería Segura RSA"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1100
        self.page.window_height = 750
        self.page.window_min_width = 900
        self.page.window_min_height = 650

        # Crear directorios
        Path("claves").mkdir(exist_ok=True)
        Path("mensajes").mkdir(exist_ok=True)

        # Inicializar campos con referencias
        self.inicializar_campos()

        # Construir interfaz
        self.construir_interfaz()

    def inicializar_campos(self):
        """Inicializa todos los campos con referencias."""
        # Campos de usuario
        self.field_crear_nombre = ft.TextField(
            label="Tu nombre",
            hint_text="Ej: alice, bob...",
        )
        self.field_crear_password = ft.TextField(
            label="Contraseña (opcional)",
            hint_text="Para proteger tu clave privada",
            password=True,
            can_reveal_password=True,
        )
        self.field_cargar_nombre = ft.TextField(
            label="Nombre de usuario",
            hint_text="Ej: profesor, alice...",
        )
        self.field_cargar_password = ft.TextField(
            label="Contraseña",
            hint_text="Si la configuraste",
            password=True,
            can_reveal_password=True,
        )

        # Campos de mensajes
        self.combo_destinatarios = ft.Dropdown(
            label="Destinatario",
            hint_text="Selecciona un contacto",
            options=[],
        )
        self.texto_mensaje = ft.TextField(
            label="Mensaje",
            hint_text="Escribe tu mensaje aquí...",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        self.texto_cifrado = ft.TextField(
            label="Mensaje Cifrado Recibido",
            hint_text="Pega aquí el mensaje cifrado que recibiste...",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        self.resultado_descifrado = ft.Container(
            content=ft.Text(
                "El mensaje descifrado aparecerá aquí",
                italic=True,
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=16,
            border_radius=8,
        )

        # Campos de contactos
        self.texto_clave_publica = ft.TextField(
            label="Tu Clave Pública",
            multiline=True,
            min_lines=5,
            max_lines=8,
            read_only=True,
        )
        self.entrada_nombre_contacto = ft.TextField(
            label="Nombre del contacto",
            hint_text="Ej: bob, alice...",
        )
        self.entrada_clave_contacto = ft.TextField(
            label="Clave Pública del Contacto",
            hint_text="Pega aquí la clave que te compartió...",
            multiline=True,
            min_lines=5,
            max_lines=8,
        )
        self.lista_contactos_view = ft.Column(spacing=8)

        # Campos de red
        self.dropdown_ip = ft.Dropdown(
            label="Selecciona tu IP",
            hint_text="Elige la interfaz de red a usar",
            options=[],
        )
        self.campo_puerto = ft.TextField(
            label="Puerto",
            value=str(PUERTO_DEFAULT),
            width=150,
        )
        self.btn_servidor = ft.ElevatedButton(
            "Iniciar Servidor",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.toggle_servidor,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY),
        )
        self.campo_ip_destino = ft.TextField(
            label="IP del destinatario",
            hint_text="Ej: 192.168.1.100",
        )
        self.campo_nombre_destino = ft.TextField(
            label="Contacto",
            hint_text="Nombre del contacto",
        )
        self.historial_red = ft.ListView(
            spacing=8,
            padding=16,
            auto_scroll=True,
            expand=True,
        )

    def construir_interfaz(self):
        """Construye la interfaz principal."""
        # Barra superior
        self.usuario_chip = ft.Chip(
            label=ft.Text("Sin usuario"),
            leading=ft.Icon(ft.icons.PERSON),
            bgcolor=ft.Colors.SURFACE_VARIANT,
        )

        self.estado_servidor_chip = ft.Chip(
            label=ft.Text("Servidor detenido"),
            leading=ft.Icon(ft.icons.CIRCLE, color=ft.Colors.RED),
            bgcolor=ft.Colors.SURFACE_VARIANT,
        )

        appbar = ft.AppBar(
            title=ft.Text("🔐 Mensajería Segura RSA", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.SURFACE_VARIANT,
            actions=[
                self.usuario_chip,
                self.estado_servidor_chip,
                ft.IconButton(
                    icon=ft.icons.HELP_OUTLINE,
                    tooltip="Ayuda",
                    on_click=self.mostrar_ayuda
                ),
            ],
        )

        # Navegación por pestañas
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Inicio",
                    icon=ft.icons.HOME,
                    content=self.crear_tab_inicio(),
                ),
                ft.Tab(
                    text="Mensajes",
                    icon=ft.icons.MESSAGE,
                    content=self.crear_tab_mensajes(),
                ),
                ft.Tab(
                    text="Contactos",
                    icon=ft.icons.CONTACTS,
                    content=self.crear_tab_contactos(),
                ),
                ft.Tab(
                    text="Red",
                    icon=ft.icons.WIFI,
                    content=self.crear_tab_red(),
                ),
            ],
            expand=1,
        )

        # Barra de estado inferior
        self.status_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.INFO_OUTLINE, size=16),
                    ft.Text("Listo", size=12),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=8,
        )

        # Layout principal
        self.page.add(
            ft.Column(
                [
                    appbar,
                    self.tabs,
                    self.status_bar,
                ],
                spacing=0,
                expand=True,
            )
        )

        # Actualizar lista de IPs
        self.actualizar_lista_ips()

    # ==================== TAB INICIO ====================
    def crear_tab_inicio(self):
        """Crea la pestaña de inicio/usuario."""
        return ft.Container(
            content=ft.Column(
                [
                    # Banner de bienvenida
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.LOCK, size=48, color=ft.Colors.PRIMARY),
                                ft.Text(
                                    "Bienvenido a Mensajería Segura",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Comunicación cifrada con RSA-2048",
                                    size=14,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=40,
                        alignment=ft.alignment.center,
                    ),

                    # Sección de usuario
                    ft.Row(
                        [
                            # Crear usuario
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.icons.PERSON_ADD, size=20),
                                                ft.Text("Crear Nuevo Usuario", size=18, weight=ft.FontWeight.BOLD),
                                            ],
                                            spacing=8,
                                        ),
                                        ft.Divider(),
                                        self.field_crear_nombre,
                                        self.field_crear_password,
                                        ft.ElevatedButton(
                                            "Crear Usuario",
                                            icon=ft.icons.ADD_CIRCLE,
                                            on_click=self.crear_usuario,
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.PRIMARY,
                                                color=ft.Colors.ON_PRIMARY,
                                            ),
                                        ),
                                    ],
                                    spacing=12,
                                ),
                                bgcolor=ft.Colors.SURFACE_VARIANT,
                                padding=20,
                                border_radius=12,
                                expand=True,
                            ),

                            # Cargar usuario
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.icons.LOGIN, size=20),
                                                ft.Text("Cargar Usuario", size=18, weight=ft.FontWeight.BOLD),
                                            ],
                                            spacing=8,
                                        ),
                                        ft.Divider(),
                                        self.field_cargar_nombre,
                                        self.field_cargar_password,
                                        ft.ElevatedButton(
                                            "Cargar Usuario",
                                            icon=ft.icons.LOGIN,
                                            on_click=self.cargar_usuario,
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.TERTIARY,
                                                color=ft.Colors.ON_TERTIARY,
                                            ),
                                        ),
                                    ],
                                    spacing=12,
                                ),
                                bgcolor=ft.Colors.SURFACE_VARIANT,
                                padding=20,
                                border_radius=12,
                                expand=True,
                            ),
                        ],
                        spacing=20,
                        expand=True,
                    ),

                    # Botón cerrar sesión
                    ft.Container(
                        content=ft.OutlinedButton(
                            "Cerrar Sesión",
                            icon=ft.icons.LOGOUT,
                            on_click=self.cerrar_sesion,
                        ),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=20),
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )

    # ==================== TAB MENSAJES ====================
    def crear_tab_mensajes(self):
        """Crea la pestaña de mensajes."""
        return ft.Container(
            content=ft.Column(
                [
                    # Banner informativo
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.INFO, color=ft.Colors.PRIMARY),
                                ft.Column(
                                    [
                                        ft.Text("Cifrado de Mensajes", weight=ft.FontWeight.BOLD),
                                        ft.Text(
                                            "Los mensajes se cifran localmente. Cópialos y envíalos por WhatsApp, email, etc.",
                                            size=12,
                                            color=ft.Colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.PRIMARY_CONTAINER,
                        padding=16,
                        border_radius=8,
                    ),

                    # Cifrar mensaje
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("📤 Enviar Mensaje Cifrado", size=18, weight=ft.FontWeight.BOLD),
                                self.combo_destinatarios,
                                self.texto_mensaje,
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Cifrar y Copiar",
                                            icon=ft.icons.LOCK,
                                            on_click=self.cifrar_mensaje,
                                            style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY),
                                        ),
                                        ft.TextButton(
                                            "Limpiar",
                                            icon=ft.icons.CLEAR,
                                            on_click=self.limpiar_mensaje,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),

                    # Descifrar mensaje
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("📥 Descifrar Mensaje Recibido", size=18, weight=ft.FontWeight.BOLD),
                                self.texto_cifrado,
                                ft.ElevatedButton(
                                    "Descifrar",
                                    icon=ft.icons.LOCK_OPEN,
                                    on_click=self.descifrar_mensaje_ui,
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.TERTIARY),
                                ),
                                ft.Text("Resultado:", size=14, weight=ft.FontWeight.BOLD),
                                self.resultado_descifrado,
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )

    # ==================== TAB CONTACTOS ====================
    def crear_tab_contactos(self):
        """Crea la pestaña de contactos."""
        return ft.Container(
            content=ft.Column(
                [
                    # Mi clave pública
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("📋 Mi Clave Pública", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "Comparte esta clave con tus contactos para que puedan enviarte mensajes",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                self.texto_clave_publica,
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Mostrar",
                                            icon=ft.icons.VISIBILITY,
                                            on_click=self.mostrar_clave_publica,
                                        ),
                                        ft.ElevatedButton(
                                            "Copiar",
                                            icon=ft.icons.COPY,
                                            on_click=self.copiar_clave_publica_ui,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),

                    # Importar contacto
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("➕ Agregar Contacto", size=18, weight=ft.FontWeight.BOLD),
                                self.entrada_nombre_contacto,
                                self.entrada_clave_contacto,
                                ft.ElevatedButton(
                                    "Guardar Contacto",
                                    icon=ft.icons.SAVE,
                                    on_click=self.importar_contacto,
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY),
                                ),
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),

                    # Lista de contactos
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("👥 Mis Contactos", size=18, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                self.lista_contactos_view,
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )

    # ==================== TAB RED ====================
    def crear_tab_red(self):
        """Crea la pestaña de configuración de red."""
        return ft.Container(
            content=ft.Column(
                [
                    # Banner informativo
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.WIFI, color=ft.Colors.PRIMARY),
                                ft.Column(
                                    [
                                        ft.Text("Red Local (LAN)", weight=ft.FontWeight.BOLD),
                                        ft.Text(
                                            "Envía mensajes directamente a otras PCs en tu red. Compatible con ZeroTier.",
                                            size=12,
                                            color=ft.Colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.TERTIARY_CONTAINER,
                        padding=16,
                        border_radius=8,
                    ),

                    # Configuración del servidor
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("🌐 Mi Servidor", size=18, weight=ft.FontWeight.BOLD),
                                self.dropdown_ip,
                                ft.Row(
                                    [
                                        self.campo_puerto,
                                        ft.ElevatedButton(
                                            "Actualizar IPs",
                                            icon=ft.icons.REFRESH,
                                            on_click=lambda _: self.actualizar_lista_ips(),
                                        ),
                                    ],
                                    spacing=12,
                                ),
                                self.btn_servidor,
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),

                    # Enviar por red
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("📡 Enviar por Red", size=18, weight=ft.FontWeight.BOLD),
                                self.campo_ip_destino,
                                self.campo_nombre_destino,
                                ft.ElevatedButton(
                                    "Enviar Mensaje",
                                    icon=ft.icons.SEND,
                                    on_click=self.enviar_por_red,
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.TERTIARY),
                                ),
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),

                    # Historial
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("📨 Mensajes Recibidos", size=18, weight=ft.FontWeight.BOLD),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            tooltip="Limpiar historial",
                                            on_click=self.limpiar_historial_ui,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Container(
                                    content=self.historial_red,
                                    height=200,
                                    bgcolor=ft.Colors.SURFACE,
                                    border_radius=8,
                                    border=ft.border.all(1, ft.Colors.OUTLINE),
                                ),
                            ],
                            spacing=12,
                        ),
                        bgcolor=ft.Colors.SURFACE_VARIANT,
                        padding=20,
                        border_radius=12,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )

    # ==================== FUNCIONES DE USUARIO ====================
    def crear_usuario(self, e):
        """Crea un nuevo usuario."""
        nombre = self.field_crear_nombre.value.strip() if self.field_crear_nombre.value else ""
        password = self.field_crear_password.value.strip() if self.field_crear_password.value else ""

        if not nombre:
            self.mostrar_error("El nombre no puede estar vacío")
            return

        try:
            clave_privada, clave_publica = generar_par_claves(2048)

            ruta_privada = f"claves/{nombre}_privada.pem"
            ruta_publica = f"claves/{nombre}_publica.pem"

            Path("claves").mkdir(exist_ok=True)

            guardar_clave_privada(clave_privada, ruta_privada, password if password else None)
            guardar_clave_publica(clave_publica, ruta_publica)

            self.mostrar_exito(f"Usuario '{nombre}' creado exitosamente!\n\nClaves guardadas en:\n{ruta_privada}\n{ruta_publica}")

            # Limpiar campos
            self.field_crear_nombre.value = ""
            self.field_crear_password.value = ""
            self.page.update()

        except Exception as ex:
            self.mostrar_error(f"Error al crear usuario: {ex}")

    def cargar_usuario(self, e):
        """Carga un usuario existente."""
        nombre = self.field_cargar_nombre.value.strip() if self.field_cargar_nombre.value else ""
        password = self.field_cargar_password.value.strip() if self.field_cargar_password.value else ""

        if not nombre:
            self.mostrar_error("El nombre no puede estar vacío")
            return

        ruta_privada = f"claves/{nombre}_privada.pem"

        if not Path(ruta_privada).exists():
            self.mostrar_error(f"No se encontró el usuario '{nombre}'")
            return

        try:
            clave_privada = cargar_clave_privada(ruta_privada, password if password else None)
            clave_publica = obtener_clave_publica_desde_privada(clave_privada)

            self.usuario_actual = {
                "nombre": nombre,
                "clave_privada": clave_privada,
                "clave_publica": clave_publica,
            }

            # Configurar gestor de red
            gestor.configurar(
                self.usuario_actual,
                self.mensaje_recibido_callback,
                self.estado_red_callback,
            )

            # Actualizar UI
            self.usuario_chip.label = ft.Text(f"Usuario: {nombre}")
            self.usuario_chip.leading = ft.Icon(ft.icons.PERSON, color=ft.Colors.GREEN)
            self.actualizar_contactos()

            self.mostrar_exito(f"¡Bienvenido {nombre}!")

            # Preguntar si quiere iniciar servidor
            def iniciar_servidor_dialog(e):
                if hasattr(e.control, 'text') and e.control.text == "Sí":
                    self.tabs.selected_index = 3  # Tab de Red
                dlg.open = False
                self.page.update()

            dlg = ft.AlertDialog(
                title=ft.Text("Iniciar Servidor"),
                content=ft.Text(f"¿Quieres iniciar el servidor para recibir mensajes?"),
                actions=[
                    ft.TextButton("Sí", on_click=iniciar_servidor_dialog),
                    ft.TextButton("Ahora no", on_click=iniciar_servidor_dialog),
                ],
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

            # Limpiar campos
            self.field_cargar_nombre.value = ""
            self.field_cargar_password.value = ""
            self.page.update()

        except Exception as ex:
            self.mostrar_error(f"Error al cargar usuario: {ex}")

    def cerrar_sesion(self, e):
        """Cierra la sesión actual."""
        self.usuario_actual = None
        self.usuario_chip.label = ft.Text("Sin usuario")
        self.usuario_chip.leading = ft.Icon(ft.icons.PERSON)

        if self.servidor_activo:
            gestor.detener_servidor()
            self.servidor_activo = False
            self.actualizar_estado_servidor()

        self.mostrar_status("Sesión cerrada")
        self.page.update()

    # ==================== FUNCIONES DE MENSAJES ====================
    def limpiar_mensaje(self, e):
        """Limpia el campo de mensaje."""
        self.texto_mensaje.value = ""
        self.page.update()

    def cifrar_mensaje(self, e):
        """Cifra un mensaje para un contacto."""
        if not self.usuario_actual:
            self.mostrar_error("Debes cargar un usuario primero")
            return

        destinatario = self.combo_destinatarios.value
        mensaje = self.texto_mensaje.value

        if not destinatario:
            self.mostrar_error("Selecciona un destinatario")
            return

        if not mensaje:
            self.mostrar_error("Escribe un mensaje")
            return

        try:
            ruta_publica = f"claves/{destinatario}_publica.pem"
            clave_publica_dest = cargar_clave_publica(ruta_publica)

            mensaje_cifrado = cifrar_mensaje(mensaje, clave_publica_dest)

            # Copiar al portapapeles
            self.page.set_clipboard(mensaje_cifrado)

            # Guardar
            Path("mensajes").mkdir(exist_ok=True)
            nombre_archivo = f"mensajes/{self.usuario_actual['nombre']}_para_{destinatario}.txt"
            Path(nombre_archivo).write_text(mensaje_cifrado, encoding='utf-8')

            self.mostrar_exito(
                f"✅ Mensaje cifrado y copiado al portapapeles!\n\n"
                f"Ahora puedes pegarlo en WhatsApp, email, etc. y enviarlo a {destinatario}"
            )

            self.texto_mensaje.value = ""
            self.page.update()

        except Exception as ex:
            self.mostrar_error(f"Error al cifrar: {ex}")

    def descifrar_mensaje_ui(self, e):
        """Descifra un mensaje recibido."""
        if not self.usuario_actual:
            self.mostrar_error("Debes cargar un usuario primero")
            return

        mensaje_cifrado = self.texto_cifrado.value

        if not mensaje_cifrado:
            self.mostrar_error("Pega el mensaje cifrado primero")
            return

        try:
            mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, self.usuario_actual["clave_privada"])

            self.resultado_descifrado.content = ft.Text(
                mensaje_descifrado,
                selectable=True,
            )

            # Guardar
            Path("mensajes").mkdir(exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"mensajes/recibido_por_{self.usuario_actual['nombre']}_{timestamp}.txt"
            Path(nombre_archivo).write_text(mensaje_descifrado, encoding='utf-8')

            self.mostrar_status("Mensaje descifrado correctamente")
            self.page.update()

        except Exception as ex:
            self.mostrar_error(f"Error al descifrar: {ex}\n\nVerifica que el mensaje fue cifrado con tu clave pública.")

    # ==================== FUNCIONES DE CONTACTOS ====================
    def mostrar_clave_publica(self, e):
        """Muestra la clave pública del usuario."""
        if not self.usuario_actual:
            self.mostrar_error("Debes cargar un usuario primero")
            return

        pem = exportar_clave_publica_pem(self.usuario_actual["clave_publica"])
        self.texto_clave_publica.value = pem
        self.page.update()

    def copiar_clave_publica_ui(self, e):
        """Copia la clave pública al portapapeles."""
        if not self.usuario_actual:
            self.mostrar_error("Debes cargar un usuario primero")
            return

        pem = exportar_clave_publica_pem(self.usuario_actual["clave_publica"])
        self.page.set_clipboard(pem)
        self.mostrar_status("Clave pública copiada al portapapeles")

    def importar_contacto(self, e):
        """Importa la clave pública de un contacto."""
        nombre = self.entrada_nombre_contacto.value.strip() if self.entrada_nombre_contacto.value else ""
        pem_clave = self.entrada_clave_contacto.value.strip() if self.entrada_clave_contacto.value else ""

        if not nombre:
            self.mostrar_error("Escribe el nombre del contacto")
            return

        if not pem_clave:
            self.mostrar_error("Pega la clave pública del contacto")
            return

        try:
            clave_publica = importar_clave_publica_pem(pem_clave)

            Path("claves").mkdir(exist_ok=True)
            ruta = f"claves/{nombre}_publica.pem"
            guardar_clave_publica(clave_publica, ruta)

            self.mostrar_exito(f"Contacto '{nombre}' guardado exitosamente!")

            self.entrada_nombre_contacto.value = ""
            self.entrada_clave_contacto.value = ""
            self.actualizar_contactos()
            self.page.update()

        except Exception as ex:
            self.mostrar_error(f"Error al importar contacto: {ex}")

    def actualizar_contactos(self):
        """Actualiza la lista de contactos."""
        contactos = []
        carpeta_claves = Path("claves")

        if carpeta_claves.exists():
            for archivo in carpeta_claves.glob("*_publica.pem"):
                nombre = archivo.stem.replace("_publica", "")
                if self.usuario_actual and nombre != self.usuario_actual["nombre"]:
                    contactos.append(nombre)

        # Actualizar dropdown
        self.combo_destinatarios.options = [
            ft.dropdown.Option(c) for c in contactos
        ]

        # Actualizar lista visual
        self.lista_contactos_view.controls.clear()
        if contactos:
            for contacto in contactos:
                self.lista_contactos_view.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.PERSON, size=20),
                                ft.Text(contacto, size=14),
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.SURFACE,
                        padding=12,
                        border_radius=8,
                    )
                )
        else:
            self.lista_contactos_view.controls.append(
                ft.Text("No hay contactos. Importa uno arriba.", italic=True, color=ft.Colors.ON_SURFACE_VARIANT)
            )

        self.page.update()

    # ==================== FUNCIONES DE RED ====================
    def actualizar_lista_ips(self):
        """Actualiza la lista de interfaces de red."""
        interfaces = obtener_todas_las_ips()

        if not interfaces:
            self.dropdown_ip.options = [
                ft.dropdown.Option(key="127.0.0.1", text="127.0.0.1 - Localhost")
            ]
            self.dropdown_ip.value = "127.0.0.1"
        else:
            self.dropdown_ip.options = [
                ft.dropdown.Option(
                    key=ip,
                    text=f"{ip} - {desc} ({nombre})"
                )
                for nombre, ip, desc in interfaces
            ]
            # Seleccionar la primera
            self.dropdown_ip.value = interfaces[0][1]

        self.page.update()

    def toggle_servidor(self, e):
        """Inicia o detiene el servidor."""
        if self.servidor_activo:
            gestor.detener_servidor()
            self.servidor_activo = False
            self.actualizar_estado_servidor()
        else:
            if not self.usuario_actual:
                self.mostrar_error("Debes cargar un usuario antes de iniciar el servidor")
                return

            try:
                puerto = int(self.campo_puerto.value)
                ip_seleccionada = self.dropdown_ip.value

                if not ip_seleccionada:
                    self.mostrar_error("Selecciona una interfaz de red")
                    return

                self.ip_seleccionada = ip_seleccionada

                gestor.configurar(
                    self.usuario_actual,
                    self.mensaje_recibido_callback,
                    self.estado_red_callback,
                )
                gestor.iniciar_servidor(puerto)
                self.servidor_activo = True
                self.actualizar_estado_servidor()
                self.mostrar_status(f"Servidor iniciado en {ip_seleccionada}:{puerto}")

            except Exception as ex:
                self.mostrar_error(f"Error al iniciar servidor: {ex}")

    def actualizar_estado_servidor(self):
        """Actualiza el estado visual del servidor."""
        if self.servidor_activo:
            self.btn_servidor.text = "Detener Servidor"
            self.btn_servidor.icon = ft.icons.STOP
            self.btn_servidor.style = ft.ButtonStyle(bgcolor=ft.Colors.ERROR)
            self.estado_servidor_chip.label = ft.Text("Servidor activo")
            self.estado_servidor_chip.leading = ft.Icon(ft.icons.CIRCLE, color=ft.Colors.GREEN)
        else:
            self.btn_servidor.text = "Iniciar Servidor"
            self.btn_servidor.icon = ft.icons.PLAY_ARROW
            self.btn_servidor.style = ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY)
            self.estado_servidor_chip.label = ft.Text("Servidor detenido")
            self.estado_servidor_chip.leading = ft.Icon(ft.icons.CIRCLE, color=ft.Colors.RED)

        self.page.update()

    def enviar_por_red(self, e):
        """Envía un mensaje por red."""
        if not self.usuario_actual:
            self.mostrar_error("Debes cargar un usuario primero")
            return

        ip = self.campo_ip_destino.value.strip() if self.campo_ip_destino.value else ""
        nombre = self.campo_nombre_destino.value.strip() if self.campo_nombre_destino.value else ""

        if not ip:
            self.mostrar_error("Ingresa la IP del destinatario")
            return

        if not nombre:
            self.mostrar_error("Ingresa el nombre del contacto")
            return

        # Verificar que existe la clave
        ruta_clave = Path(f"claves/{nombre}_publica.pem")
        if not ruta_clave.exists():
            self.mostrar_error(f"No tienes la clave pública de '{nombre}'.\nImportala en la pestaña Contactos primero.")
            return

        # Diálogo para el mensaje
        mensaje_field = ft.TextField(
            label="Mensaje",
            multiline=True,
            min_lines=3,
            max_lines=5,
            autofocus=True,
        )

        def enviar_mensaje_dialog(e):
            mensaje = mensaje_field.value.strip() if mensaje_field.value else ""
            if not mensaje:
                return

            dlg_mensaje.open = False
            self.page.update()

            try:
                exito = gestor.enviar_a(ip, mensaje, nombre)
                if exito:
                    self.mostrar_exito(f"Mensaje enviado a {nombre} ({ip})")
                else:
                    self.mostrar_error("No se pudo enviar el mensaje.\nVerifica que el destinatario tenga el servidor activo.")
            except Exception as ex:
                self.mostrar_error(f"Error al enviar: {ex}")

        def cancelar_dialog(e):
            dlg_mensaje.open = False
            self.page.update()

        dlg_mensaje = ft.AlertDialog(
            title=ft.Text(f"Enviar mensaje a {nombre}"),
            content=ft.Container(
                content=mensaje_field,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_dialog),
                ft.ElevatedButton("Enviar", on_click=enviar_mensaje_dialog),
            ],
        )

        self.page.dialog = dlg_mensaje
        dlg_mensaje.open = True
        self.page.update()

    def mensaje_recibido_callback(self, data: dict):
        """Callback cuando se recibe un mensaje por red."""
        if data.get('tipo') == 'recibido_cifrado':
            origen = data.get('origen', 'desconocido')
            mensaje = data.get('mensaje_descifrado', '')

            timestamp = time.strftime("%H:%M:%S")

            # Agregar al historial
            self.historial_red.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.MESSAGE, size=16, color=ft.Colors.PRIMARY),
                                    ft.Text(f"De: {origen}", weight=ft.FontWeight.BOLD, size=12),
                                    ft.Text(timestamp, size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                                ],
                                spacing=8,
                            ),
                            ft.Text(mensaje, size=13, selectable=True),
                        ],
                        spacing=4,
                    ),
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    padding=12,
                    border_radius=8,
                )
            )

            self.page.update()

            # Notificación
            self.mostrar_snackbar(f"📨 Mensaje de {origen}")

    def estado_red_callback(self, mensaje: str):
        """Callback para estado de red."""
        self.mostrar_status(mensaje)

    def limpiar_historial_ui(self, e):
        """Limpia el historial de mensajes de red."""
        self.historial_red.controls.clear()
        self.page.update()

    # ==================== FUNCIONES DE UI ====================
    def mostrar_error(self, mensaje: str):
        """Muestra un diálogo de error."""
        def cerrar_dialog(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("OK", on_click=cerrar_dialog)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def mostrar_exito(self, mensaje: str):
        """Muestra un diálogo de éxito."""
        def cerrar_dialog(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Éxito"),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("OK", on_click=cerrar_dialog)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def mostrar_snackbar(self, mensaje: str):
        """Muestra una notificación snackbar."""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(mensaje))
        self.page.snack_bar.open = True
        self.page.update()

    def mostrar_status(self, mensaje: str):
        """Actualiza la barra de estado."""
        self.status_bar.content = ft.Row(
            [
                ft.Icon(ft.icons.INFO_OUTLINE, size=16),
                ft.Text(mensaje, size=12),
            ],
            spacing=8,
        )
        self.page.update()

    def mostrar_ayuda(self, e):
        """Muestra el diálogo de ayuda."""
        ayuda_text = """
📖 Guía Rápida

1️⃣ INICIO:
   • Crea tu usuario o carga uno existente
   • Se generan automáticamente tus claves RSA

2️⃣ MENSAJES:
   • Selecciona un contacto
   • Escribe y cifra tu mensaje
   • Se copia al portapapeles (pégalo en WhatsApp, email, etc.)
   • Para descifrar: pega el mensaje cifrado recibido

3️⃣ CONTACTOS:
   • Comparte tu clave pública
   • Importa las claves de tus contactos

4️⃣ RED LOCAL:
   • Selecciona tu interfaz de red (WiFi, Ethernet, ZeroTier...)
   • Inicia el servidor para recibir mensajes
   • Envía mensajes directos a otras PCs
   • Compatible con ZeroTier para conexiones remotas
        """

        def cerrar_ayuda(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Ayuda"),
            content=ft.Container(
                content=ft.Text(ayuda_text, selectable=True),
                width=500,
            ),
            actions=[ft.TextButton("Cerrar", on_click=cerrar_ayuda)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()


def main(page: ft.Page):
    """Función principal de la aplicación Flet."""
    app = MensajeriaApp(page)


if __name__ == "__main__":
    ft.app(target=main)
