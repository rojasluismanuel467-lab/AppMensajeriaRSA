"""
Utilidades para el cifrado y descifrado RSA
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64
import re


class CryptoManager:
    """Maneja la generación de claves y el cifrado/descifrado RSA"""

    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        """Genera un par de claves RSA"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        return self.get_public_key_string()

    def get_public_key_string(self):
        """Obtiene la clave pública como string en formato PEM"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    @staticmethod
    def clean_public_key(public_key_pem):
        """
        Limpia y normaliza una clave pública PEM

        Args:
            public_key_pem (str): Clave pública que puede tener formato incorrecto

        Returns:
            str: Clave pública limpia en formato PEM correcto

        Raises:
            ValueError: Si la clave no es válida
        """
        if not public_key_pem or not isinstance(public_key_pem, str):
            raise ValueError("La clave pública no puede estar vacía")

        # Eliminar espacios en blanco al inicio y final
        key = public_key_pem.strip()

        # Eliminar posibles espacios extras entre líneas
        key = '\n'.join(line.strip() for line in key.split('\n') if line.strip())

        # Verificar que tenga el header y footer
        has_header = '-----BEGIN PUBLIC KEY-----' in key
        has_footer = '-----END PUBLIC KEY-----' in key

        if not has_header or not has_footer:
            raise ValueError(
                "La clave pública debe contener:\n"
                "-----BEGIN PUBLIC KEY-----\n"
                "...\n"
                "-----END PUBLIC KEY-----"
            )

        # Normalizar saltos de línea (Windows -> Unix)
        key = key.replace('\r\n', '\n').replace('\r', '\n')

        # Asegurar que el header y footer estén en líneas separadas
        key = key.replace('-----BEGIN PUBLIC KEY-----', '-----BEGIN PUBLIC KEY-----\n')
        key = key.replace('-----END PUBLIC KEY-----', '\n-----END PUBLIC KEY-----')

        # Limpiar líneas vacías múltiples
        key = re.sub(r'\n\n+', '\n', key)

        # Asegurar que termina con salto de línea
        if not key.endswith('\n'):
            key += '\n'

        return key

    def encrypt_message(self, message, public_key_pem):
        """
        Cifra un mensaje usando la clave pública proporcionada

        Args:
            message (str): Mensaje a cifrar
            public_key_pem (str): Clave pública en formato PEM

        Returns:
            str: Mensaje cifrado en base64

        Raises:
            ValueError: Si la clave pública no es válida
        """
        # Limpiar y validar la clave pública
        try:
            cleaned_key = self.clean_public_key(public_key_pem)
        except ValueError as e:
            raise ValueError(f"Error en formato de clave pública: {str(e)}")

        # Cargar la clave pública desde el string PEM
        try:
            public_key = serialization.load_pem_public_key(
                cleaned_key.encode('utf-8'),
                backend=default_backend()
            )
        except Exception as e:
            raise ValueError(
                f"No se pudo cargar la clave pública. "
                f"Asegúrate de copiar la clave completa incluyendo:\n"
                f"-----BEGIN PUBLIC KEY-----\n"
                f"...\n"
                f"-----END PUBLIC KEY-----\n"
                f"Error: {str(e)}"
            )

        # Cifrar el mensaje
        encrypted = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Convertir a base64 para facilitar la transmisión
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_message(self, encrypted_message_b64):
        """
        Descifra un mensaje usando la clave privada

        Args:
            encrypted_message_b64 (str): Mensaje cifrado en base64

        Returns:
            str: Mensaje descifrado
        """
        if not self.private_key:
            raise ValueError("No se ha generado una clave privada")

        # Decodificar desde base64
        encrypted = base64.b64decode(encrypted_message_b64)

        # Descifrar el mensaje
        decrypted = self.private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return decrypted.decode('utf-8')

    def save_keys(self, private_key_file='private_key.pem', public_key_file='public_key.pem'):
        """Guarda las claves en archivos"""
        if not self.private_key:
            raise ValueError("No se ha generado una clave privada")

        # Guardar clave privada
        with open(private_key_file, 'wb') as f:
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            f.write(pem)

        # Guardar clave pública
        with open(public_key_file, 'wb') as f:
            pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            f.write(pem)

    def load_keys(self, private_key_file='private_key.pem'):
        """Carga las claves desde archivos"""
        with open(private_key_file, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
