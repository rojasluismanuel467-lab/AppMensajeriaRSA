"""
Aplicación de Mensajería Segura con RSA (Versión Consola).
Permite enviar y recibir mensajes cifrados entre dos usuarios.
"""

import os
from pathlib import Path
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


CARPETA_CLAVES = "claves"
CARPETA_MENSAJES = "mensajes"


def inicializar_directorios():
    """Crea los directorios necesarios para la aplicación."""
    Path(CARPETA_CLAVES).mkdir(exist_ok=True)
    Path(CARPETA_MENSAJES).mkdir(exist_ok=True)


def mostrar_menu():
    """Muestra el menú principal de la aplicación."""
    print("\n" + "=" * 50)
    print("   APLICACIÓN DE MENSAJERÍA SEGURA CON RSA")
    print("=" * 50)
    print("\n1. Generar nuevo par de claves (nuevo usuario)")
    print("2. Cargar clave privada existente")
    print("3. Ver mi clave pública")
    print("4. Importar clave pública de otro usuario")
    print("5. Cifrar y enviar mensaje")
    print("6. Descifrar mensaje recibido")
    print("7. Ver mensajes guardados")
    print("8. Salir")
    print("=" * 50)


def generar_nuevo_usuario():
    """Genera un nuevo par de claves para un usuario."""
    print("\n--- Generar Nuevo Usuario ---")
    nombre_usuario = input("Nombre del usuario: ").strip()
    
    if not nombre_usuario:
        print("Error: El nombre no puede estar vacío.")
        return
    
    tamano_clave = input("Tamaño de clave (2048 recomendado, Enter para default): ").strip()
    tamano_clave = int(tamano_clave) if tamano_clave else 2048
    
    try:
        clave_privada, clave_publica = generar_par_claves(tamano_clave)
        
        # Guardar claves
        ruta_privada = f"{CARPETA_CLAVES}/{nombre_usuario}_privada.pem"
        ruta_publica = f"{CARPETA_CLAVES}/{nombre_usuario}_publica.pem"
        
        contrasena = input("Contraseña para proteger clave privada (opcional, Enter para none): ").strip()
        contrasena = contrasena if contrasena else None
        
        guardar_clave_privada(clave_privada, ruta_privada, contrasena)
        guardar_clave_publica(clave_publica, ruta_publica)
        
        print(f"\n✓ Claves generadas exitosamente para '{nombre_usuario}'")
        print(f"  - Clave privada: {ruta_privada}")
        print(f"  - Clave pública: {ruta_publica}")
        print("\n⚠️  IMPORTANTE: Comparte tu clave pública con quien quieras recibir mensajes.")
        print("    ¡NUNCA compartas tu clave privada!")
        
    except Exception as e:
        print(f"Error al generar claves: {e}")


def cargar_usuario():
    """Carga un usuario existente desde su clave privada."""
    print("\n--- Cargar Usuario Existente ---")
    nombre_usuario = input("Nombre del usuario: ").strip()
    
    ruta_privada = f"{CARPETA_CLAVES}/{nombre_usuario}_privada.pem"
    
    if not Path(ruta_privada).exists():
        print(f"Error: No se encontró la clave privada para '{nombre_usuario}'")
        return None
    
    contrasena = input("Contraseña de la clave privada (Enter si no tiene): ").strip()
    contrasena = contrasena if contrasena else None
    
    try:
        clave_privada = cargar_clave_privada(ruta_privada, contrasena)
        clave_publica = obtener_clave_publica_desde_privada(clave_privada)
        
        print(f"\n✓ Usuario '{nombre_usuario}' cargado exitosamente")
        
        return {
            "nombre": nombre_usuario,
            "clave_privada": clave_privada,
            "clave_publica": clave_publica,
        }
    except Exception as e:
        print(f"Error al cargar la clave privada: {e}")
        return None


def ver_clave_publica(usuario):
    """Muestra la clave pública del usuario actual."""
    print("\n--- Tu Clave Pública ---")
    pem_publica = exportar_clave_publica_pem(usuario["clave_publica"])
    print(pem_publica)
    print("\n💡 Copia esta clave y compártela con quien quieras recibir mensajes.")


def importar_clave_publica():
    """Importa la clave pública de otro usuario."""
    print("\n--- Importar Clave Pública de Contacto ---")
    nombre_contacto = input("Nombre del contacto: ").strip()
    
    if not nombre_contacto:
        print("Error: El nombre no puede estar vacío.")
        return
    
    print("\nPega la clave pública PEM del contacto (termina con línea vacía):")
    lineas = []
    while True:
        linea = input()
        if linea.strip() == "":
            break
        lineas.append(linea)
    
    pem_clave = "\n".join(lineas)
    
    try:
        clave_publica = importar_clave_publica_pem(pem_clave)
        ruta_guardado = f"{CARPETA_CLAVES}/{nombre_contacto}_publica.pem"
        guardar_clave_publica(clave_publica, ruta_guardado)
        
        print(f"\n✓ Clave pública de '{nombre_contacto}' guardada en {ruta_guardado}")
        
    except Exception as e:
        print(f"Error al importar clave pública: {e}")


def enviar_mensaje(usuario, contactos):
    """Cifra y envía un mensaje a otro usuario."""
    print("\n--- Enviar Mensaje Cifrado ---")
    
    if not contactos:
        print("No hay contactos disponibles. Importa una clave pública primero.")
        return
    
    print("\nContactos disponibles:")
    for i, nombre in enumerate(contactos, 1):
        print(f"  {i}. {nombre}")
    
    try:
        opcion = int(input("\nSelecciona un contacto (número): "))
        if opcion < 1 or opcion > len(contactos):
            print("Opción inválida.")
            return
        nombre_destinatario = contactos[opcion - 1]
    except ValueError:
        print("Error: Debes ingresar un número válido.")
        return
    
    # Cargar clave pública del destinatario
    ruta_publica_destinatario = f"{CARPETA_CLAVES}/{nombre_destinatario}_publica.pem"
    
    try:
        clave_publica_destinatario = cargar_clave_publica(ruta_publica_destinatario)
    except Exception as e:
        print(f"Error al cargar la clave del destinatario: {e}")
        return
    
    mensaje = input("\nEscribe tu mensaje: ").strip()
    
    if not mensaje:
        print("Error: El mensaje no puede estar vacío.")
        return
    
    try:
        mensaje_cifrado = cifrar_mensaje(mensaje, clave_publica_destinatario)
        
        # Guardar mensaje cifrado
        nombre_archivo = f"{usuario['nombre']}_para_{nombre_destinatario}_{len(os.listdir(CARPETA_MENSAJES))}.txt"
        ruta_mensaje = f"{CARPETA_MENSAJES}/{nombre_archivo}"
        Path(ruta_mensaje).write_text(mensaje_cifrado, encoding='utf-8')
        
        print(f"\n✓ Mensaje cifrado y guardado en: {ruta_mensaje}")
        print("\n📤 Mensaje cifrado (Base64):")
        print("-" * 50)
        print(mensaje_cifrado[:200] + "..." if len(mensaje_cifrado) > 200 else mensaje_cifrado)
        print("-" * 50)
        print("\n💡 Envía este texto cifrado al destinatario por cualquier medio.")
        
    except Exception as e:
        print(f"Error al cifrar el mensaje: {e}")


def recibir_mensaje(usuario):
    """Descifra un mensaje recibido."""
    print("\n--- Descifrar Mensaje Recibido ---")
    
    print("\nPega el mensaje cifrado (Base64):")
    mensaje_cifrado = input().strip()
    
    if not mensaje_cifrado:
        print("Error: No se proporcionó ningún mensaje cifrado.")
        return
    
    try:
        mensaje_descifrado = descifrar_mensaje(mensaje_cifrado, usuario["clave_privada"])
        
        print("\n" + "=" * 50)
        print("   MENSAJE DESCIFRADO")
        print("=" * 50)
        print(mensaje_descifrado)
        print("=" * 50)
        
        # Guardar mensaje descifrado
        nombre_archivo = f"recibido_por_{usuario['nombre']}_{len(os.listdir(CARPETA_MENSAJES))}.txt"
        ruta_guardado = f"{CARPETA_MENSAJES}/{nombre_archivo}"
        Path(ruta_guardado).write_text(mensaje_descifrado, encoding='utf-8')
        print(f"\n✓ Mensaje guardado en: {ruta_guardado}")
        
    except Exception as e:
        print(f"Error al descifrar el mensaje: {e}")
        print("⚠️  Verifica que el mensaje fue cifrado con tu clave pública.")


def ver_mensajes_guardados():
    """Muestra los mensajes guardados en la carpeta de mensajes."""
    print("\n--- Mensajes Guardados ---")
    
    mensajes = list(Path(CARPETA_MENSAJES).glob("*.txt"))
    
    if not mensajes:
        print("No hay mensajes guardados.")
        return
    
    for i, archivo in enumerate(mensajes, 1):
        print(f"  {i}. {archivo.name}")
    
    try:
        opcion = int(input("\nSelecciona un mensaje para ver su contenido (0 para salir): "))
        if opcion == 0:
            return
        if opcion < 1 or opcion > len(mensajes):
            print("Opción inválida.")
            return
        
        contenido = mensajes[opcion - 1].read_text(encoding='utf-8')
        print("\n" + "-" * 50)
        print(contenido[:500] + "..." if len(contenido) > 500 else contenido)
        print("-" * 50)
        
    except ValueError:
        print("Error: Debes ingresar un número válido.")


def obtener_contactos_disponibles(usuario_nombre):
    """Obtiene la lista de contactos (claves públicas) disponibles."""
    contactos = []
    for archivo in Path(CARPETA_CLAVES).glob("*_publica.pem"):
        nombre_contacto = archivo.stem.replace("_publica", "")
        if nombre_contacto != usuario_nombre:
            contactos.append(nombre_contacto)
    return contactos


def main():
    """Función principal de la aplicación."""
    inicializar_directorios()
    
    usuario_actual = None
    
    while True:
        mostrar_menu()
        
        if usuario_actual:
            print(f"Usuario actual: {usuario_actual['nombre']}")
        else:
            print("Usuario actual: Ninguno (debes cargar o crear un usuario)")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            generar_nuevo_usuario()
        
        elif opcion == "2":
            usuario_actual = cargar_usuario()
        
        elif opcion == "3":
            if usuario_actual:
                ver_clave_publica(usuario_actual)
            else:
                print("⚠️  Primero debes cargar o crear un usuario.")
        
        elif opcion == "4":
            importar_clave_publica()
        
        elif opcion == "5":
            if usuario_actual:
                contactos = obtener_contactos_disponibles(usuario_actual["nombre"])
                enviar_mensaje(usuario_actual, contactos)
            else:
                print("⚠️  Primero debes cargar o crear un usuario.")
        
        elif opcion == "6":
            if usuario_actual:
                recibir_mensaje(usuario_actual)
            else:
                print("⚠️  Primero debes cargar o crear un usuario.")
        
        elif opcion == "7":
            ver_mensajes_guardados()
        
        elif opcion == "8":
            print("\n¡Hasta luego!")
            break
        
        else:
            print("Opción inválida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
