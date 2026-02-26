from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64
import re


class CryptoManager:

    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        return self.get_public_key_string()

    def get_public_key_string(self):
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    @staticmethod
    def clean_public_key(public_key_pem):
        if not public_key_pem or not isinstance(public_key_pem, str):
            raise ValueError("La clave pública no puede estar vacía")

        key = public_key_pem.strip()
        key = '\n'.join(line.strip() for line in key.split('\n') if line.strip())

        has_header = '-----BEGIN PUBLIC KEY-----' in key
        has_footer = '-----END PUBLIC KEY-----' in key

        if not has_header or not has_footer:
            raise ValueError(
                "La clave pública debe contener:\n"
                "-----BEGIN PUBLIC KEY-----\n"
                "...\n"
                "-----END PUBLIC KEY-----"
            )

        key = key.replace('\r\n', '\n').replace('\r', '\n')
        key = key.replace('-----BEGIN PUBLIC KEY-----', '-----BEGIN PUBLIC KEY-----\n')
        key = key.replace('-----END PUBLIC KEY-----', '\n-----END PUBLIC KEY-----')
        key = re.sub(r'\n\n+', '\n', key)

        if not key.endswith('\n'):
            key += '\n'

        return key

    def encrypt_message(self, message, public_key_pem):
        try:
            cleaned_key = self.clean_public_key(public_key_pem)
        except ValueError as e:
            raise ValueError(f"Error en formato de clave pública: {str(e)}")

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

        encrypted = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_message(self, encrypted_message_b64):
        if not self.private_key:
            raise ValueError("No se ha generado una clave privada")

        encrypted = base64.b64decode(encrypted_message_b64)

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
        if not self.private_key:
            raise ValueError("No se ha generado una clave privada")

        with open(private_key_file, 'wb') as f:
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            f.write(pem)

        with open(public_key_file, 'wb') as f:
            pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            f.write(pem)

    def load_keys(self, private_key_file='private_key.pem'):
        with open(private_key_file, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
