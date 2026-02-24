"""
Aplicación de Mensajería Segura con RSA.
Punto de entrada principal.
"""

import sys


def iniciar_gui():
    """Inicia la interfaz gráfica."""
    from gui import main
    main()


def iniciar_consola():
    """Inicia la interfaz de consola (versión anterior)."""
    from main_console import main
    main()


if __name__ == "__main__":
    # Por defecto, iniciar GUI
    if len(sys.argv) > 1 and sys.argv[1] == "--consola":
        iniciar_consola()
    else:
        iniciar_gui()
