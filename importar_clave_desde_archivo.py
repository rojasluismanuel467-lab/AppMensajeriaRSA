#!/usr/bin/env python3
"""
Script para importar la clave privada del profesor desde un archivo PEM.
Uso: python importar_clave_desde_archivo.py ruta/al/archivo.pem
"""

import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pathlib import Path


def importar_clave(ruta_archivo: str):
    """Importa clave privada desde archivo y genera la pública."""
    
    if not Path(ruta_archivo).exists():
        print(f"ERROR: El archivo '{ruta_archivo}' no existe.")
        return False
    
    try:
        # Leer archivo
        pem_data = Path(ruta_archivo).read_bytes()
        
        # Cargar clave privada
        clave_privada = serialization.load_pem_private_key(
            pem_data,
            password=None,
            backend=default_backend()
        )
        
        print(f"EXITO: Clave cargada correctamente")
        print(f"  - Tipo: RSA")
        print(f"  - Tamano: {clave_privada.key_size} bits")
        
        # Extraer clave pública
        clave_publica = clave_privada.public_key()
        
        # Crear directorio de claves
        Path("claves").mkdir(exist_ok=True)
        
        # Guardar clave privada (copiar archivo)
        ruta_destino_privada = "claves/profesor_privada.pem"
        Path(ruta_destino_privada).write_bytes(pem_data)
        print(f"\nClave privada copiada a: {ruta_destino_privada}")
        
        # Guardar clave pública
        pem_publica = clave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        ruta_destino_publica = "claves/profesor_publica.pem"
        Path(ruta_destino_publica).write_bytes(pem_publica)
        print(f"Clave pública generada en: {ruta_destino_publica}")
        
        # Mostrar clave pública
        print("\n" + "=" * 60)
        print("CLAVE PUBLICA (compartir con otros usuarios):")
        print("=" * 60)
        print(pem_publica.decode('utf-8'))
        print("=" * 60)
        
        print("\nInstrucciones:")
        print("  1. Ejecuta: python main.py")
        print("  2. Selecciona opcion 2: Cargar clave privada existente")
        print("  3. Ingresa el nombre: profesor")
        print("  4. Ahora puedes recibir mensajes cifrados!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nPosibles causas:")
        print("  1. El archivo no es una clave RSA valida")
        print("  2. La clave esta corrupta o incompleta")
        print("  3. La clave requiere contrasena")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  IMPORTAR CLAVE RSA DEL PROFESOR")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUso: python importar_clave_desde_archivo.py <ruta_al_archivo.pem>")
        print("\nEjemplo:")
        print("  python importar_clave_desde_archivo.py private-key.pem")
        print("\nSi tienes el archivo private-key.pem, copialo a esta carpeta")
        print("y ejecuta el comando anterior.")
    else:
        importar_clave(sys.argv[1])
