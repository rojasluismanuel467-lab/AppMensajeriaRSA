"""
Módulo para cifrado y descifrado de mensajes usando RSA.
Implementa el algoritmo RSA con OAEP (Optimal Asymmetric Encryption Padding).
"""

import base64
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


def cifrar_mensaje(mensaje: str, clave_publica) -> str:
    """
    Cifra un mensaje usando RSA con OAEP.
    
    El mensaje se cifra con la clave pública del destinatario,
    solo quien tenga la clave privada correspondiente podrá descifrarlo.
    
    Args:
        mensaje: Texto plano a cifrar
        clave_publica: Clave pública RSA del destinatario
    
    Returns:
        str: Mensaje cifrado en formato Base64
    """
    mensaje_bytes = mensaje.encode('utf-8')
    
    # RSA tiene un límite de tamaño según la clave. Para mensajes largos,
    # se podría implementar cifrado híbrido (RSA + AES)
    tamano_clave_bytes = clave_publica.key_size // 8
    tamano_maximo_mensaje = tamano_clave_bytes - 2 * 32 - 2  # OAEP con SHA-256
    
    if len(mensaje_bytes) > tamano_maximo_mensaje:
        raise ValueError(
            f"Mensaje demasiado largo. Máximo {tamano_maximo_mensaje} bytes "
            f"para clave de {clave_publica.key_size} bits. "
            f"Considere usar cifrado híbrido para mensajes largos."
        )
    
    mensaje_cifrado = clave_publica.encrypt(
        mensaje_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return base64.b64encode(mensaje_cifrado).decode('utf-8')


def descifrar_mensaje(mensaje_cifrado_b64: str, clave_privada) -> str:
    """
    Descifra un mensaje usando RSA con OAEP.
    
    El mensaje se descifra con la clave privada del receptor,
    que debe corresponder con la clave pública usada para cifrar.
    
    Args:
        mensaje_cifrado_b64: Mensaje cifrado en formato Base64
        clave_privada: Clave privada RSA del receptor
    
    Returns:
        str: Mensaje descifrado en texto plano
    """
    mensaje_cifrado = base64.b64decode(mensaje_cifrado_b64)
    
    mensaje_descifrado = clave_privada.decrypt(
        mensaje_cifrado,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return mensaje_descifrado.decode('utf-8')


def cifrar_mensaje_archivo(ruta_archivo: str, clave_publica, ruta_salida: str):
    """
    Cifra el contenido de un archivo usando RSA.
    
    Args:
        ruta_archivo: Ruta del archivo a cifrar
        clave_publica: Clave pública RSA del destinatario
        ruta_salida: Ruta donde guardar el archivo cifrado
    """
    contenido = Path(ruta_archivo).read_text(encoding='utf-8')
    contenido_cifrado = cifrar_mensaje(contenido, clave_publica)
    Path(ruta_salida).write_text(contenido_cifrado, encoding='utf-8')


def descifrar_mensaje_archivo(ruta_archivo_cifrado: str, clave_privada, ruta_salida: str):
    """
    Descifra el contenido de un archivo usando RSA.
    
    Args:
        ruta_archivo_cifrado: Ruta del archivo cifrado
        clave_privada: Clave privada RSA del receptor
        ruta_salida: Ruta donde guardar el archivo descifrado
    """
    contenido_cifrado = Path(ruta_archivo_cifrado).read_text(encoding='utf-8')
    contenido_descifrado = descifrar_mensaje(contenido_cifrado, clave_privada)
    Path(ruta_salida).write_text(contenido_descifrado, encoding='utf-8')
