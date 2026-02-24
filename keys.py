"""
Módulo para la gestión de claves RSA.
Generación, almacenamiento y carga de claves públicas y privadas.
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pathlib import Path


def generar_par_claves(tamano_clave: int = 2048):
    """
    Genera un par de claves RSA (pública y privada).
    
    Args:
        tamano_clave: Tamaño de la clave en bits (mínimo 1024, recomendado 2048 o superior)
    
    Returns:
        tuple: (clave_privada, clave_publica)
    """
    if tamano_clave < 1024:
        raise ValueError("El tamaño de clave mínimo es 1024 bits")
    
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=tamano_clave,
        backend=default_backend()
    )
    clave_publica = clave_privada.public_key()
    
    return clave_privada, clave_publica


def guardar_clave_privada(clave_privada, ruta_archivo: str, contrasena: str = None):
    """
    Guarda una clave privada en un archivo PEM.
    
    Args:
        clave_privada: Objeto de clave privada RSA
        ruta_archivo: Ruta donde guardar la clave
        contrasena: Contraseña opcional para cifrar la clave privada
    """
    algoritmo_cifrado = serialization.BestAvailableEncryption(contrasena.encode()) if contrasena else serialization.NoEncryption()
    
    pem_clave_privada = clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=algoritmo_cifrado
    )
    
    Path(ruta_archivo).write_bytes(pem_clave_privada)


def guardar_clave_publica(clave_publica, ruta_archivo: str):
    """
    Guarda una clave pública en un archivo PEM.
    
    Args:
        clave_publica: Objeto de clave pública RSA
        ruta_archivo: Ruta donde guardar la clave
    """
    pem_clave_publica = clave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    Path(ruta_archivo).write_bytes(pem_clave_publica)


def cargar_clave_privada(ruta_archivo: str, contrasena: str = None):
    """
    Carga una clave privada desde un archivo PEM.
    
    Args:
        ruta_archivo: Ruta del archivo con la clave privada
        contrasena: Contraseña si la clave está cifrada
    
    Returns:
        Objeto de clave privada RSA
    """
    pem_clave_privada = Path(ruta_archivo).read_bytes()
    
    return serialization.load_pem_private_key(
        pem_clave_privada,
        password=contrasena.encode() if contrasena else None,
        backend=default_backend()
    )


def cargar_clave_publica(ruta_archivo: str):
    """
    Carga una clave pública desde un archivo PEM.
    
    Args:
        ruta_archivo: Ruta del archivo con la clave pública
    
    Returns:
        Objeto de clave pública RSA
    """
    pem_clave_publica = Path(ruta_archivo).read_bytes()
    
    return serialization.load_pem_public_key(
        pem_clave_publica,
        backend=default_backend()
    )


def obtener_clave_publica_desde_privada(clave_privada):
    """
    Extrae la clave pública desde una clave privada RSA.
    
    Args:
        clave_privada: Objeto de clave privada RSA
    
    Returns:
        Objeto de clave pública RSA
    """
    return clave_privada.public_key()


def exportar_clave_publica_pem(clave_publica) -> str:
    """
    Exporta una clave pública a formato PEM (string).
    
    Args:
        clave_publica: Objeto de clave pública RSA
    
    Returns:
        str: Clave pública en formato PEM
    """
    pem = clave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode('utf-8')


def importar_clave_publica_pem(pem_clave_publica: str):
    """
    Importa una clave pública desde formato PEM (string).
    
    Args:
        pem_clave_publica: Clave pública en formato PEM
    
    Returns:
        Objeto de clave pública RSA
    """
    return serialization.load_pem_public_key(
        pem_clave_publica.encode('utf-8'),
        backend=default_backend()
    )
