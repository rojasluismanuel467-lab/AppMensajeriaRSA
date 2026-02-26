"""
Aplicación de mensajería cifrada con RSA
"""
from flask import Flask, render_template, request, jsonify
import requests
import os
import socket
import platform
from crypto_utils import CryptoManager

app = Flask(__name__)
crypto_manager = CryptoManager()

# Almacenar mensajes recibidos
messages = []

# Puerto de la aplicación
PORT = 5000


def get_all_ip_addresses():
    """
    Obtiene todas las direcciones IP de las interfaces de red activas
    Incluye WiFi, Ethernet, ZeroTier, etc.
    """
    ip_addresses = []
    hostname = socket.gethostname()

    try:
        # Obtener todas las interfaces de red
        addrs = socket.getaddrinfo(hostname, None)

        # Filtrar solo direcciones IPv4 únicas
        seen = set()
        for addr in addrs:
            ip = addr[4][0]
            # Filtrar direcciones IPv4 válidas (no localhost, no IPv6)
            if ':' not in ip and not ip.startswith('127.'):
                if ip not in seen:
                    seen.add(ip)

                    # Intentar determinar el tipo de interfaz
                    interface_type = "Desconocida"
                    if ip.startswith('192.168.'):
                        interface_type = "Red Local (WiFi/Ethernet)"
                    elif ip.startswith('10.'):
                        interface_type = "Red Local / ZeroTier"
                    elif ip.startswith('172.'):
                        interface_type = "Red Local"

                    ip_addresses.append({
                        'ip': ip,
                        'type': interface_type
                    })

    except Exception as e:
        print(f"Error obteniendo direcciones IP: {e}")

    # Si no se encontraron IPs, intentar método alternativo
    if not ip_addresses:
        try:
            # Conectar a una dirección externa para obtener la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            ip_addresses.append({
                'ip': ip,
                'type': "Red Principal"
            })
        except:
            pass

    return ip_addresses


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/generate-keys', methods=['POST'])
def generate_keys():
    """Genera un nuevo par de claves RSA"""
    try:
        public_key = crypto_manager.generate_keys()
        # Guardar las claves en archivos
        crypto_manager.save_keys()
        return jsonify({
            'success': True,
            'public_key': public_key
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/get-public-key', methods=['GET'])
def get_public_key():
    """Obtiene la clave pública actual"""
    try:
        if crypto_manager.public_key:
            public_key = crypto_manager.get_public_key_string()
        else:
            # Intentar cargar desde archivo
            if os.path.exists('private_key.pem'):
                crypto_manager.load_keys()
                public_key = crypto_manager.get_public_key_string()
            else:
                return jsonify({
                    'success': False,
                    'error': 'No hay claves generadas. Por favor genera claves primero.'
                }), 400

        return jsonify({
            'success': True,
            'public_key': public_key
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Envía un mensaje cifrado a otro usuario"""
    try:
        data = request.json
        message = data.get('message')
        recipient_ip = data.get('recipient_ip')
        recipient_port = data.get('recipient_port', PORT)
        recipient_public_key = data.get('recipient_public_key')

        if not all([message, recipient_ip, recipient_public_key]):
            return jsonify({
                'success': False,
                'error': 'Faltan datos requeridos'
            }), 400

        # Cifrar el mensaje con la clave pública del destinatario
        encrypted_message = crypto_manager.encrypt_message(message, recipient_public_key)

        # Enviar el mensaje cifrado al destinatario
        url = f'http://{recipient_ip}:{recipient_port}/api/receive-message'
        response = requests.post(url, json={
            'encrypted_message': encrypted_message
        }, timeout=5)

        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Mensaje enviado correctamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error al enviar el mensaje'
            }), 500

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Error de conexión: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/receive-message', methods=['POST'])
def receive_message():
    """Recibe un mensaje cifrado y lo descifra"""
    try:
        data = request.json
        encrypted_message = data.get('encrypted_message')

        if not encrypted_message:
            return jsonify({
                'success': False,
                'error': 'No se recibió el mensaje'
            }), 400

        # Verificar que tenemos claves
        if not crypto_manager.private_key:
            if os.path.exists('private_key.pem'):
                crypto_manager.load_keys()
            else:
                return jsonify({
                    'success': False,
                    'error': 'No hay claves para descifrar'
                }), 400

        # Descifrar el mensaje
        decrypted_message = crypto_manager.decrypt_message(encrypted_message)

        # Guardar el mensaje
        messages.append({
            'message': decrypted_message,
            'from_ip': request.remote_addr
        })

        return jsonify({
            'success': True,
            'message': 'Mensaje recibido y descifrado'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al descifrar: {str(e)}'
        }), 500


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Obtiene los mensajes recibidos"""
    return jsonify({
        'success': True,
        'messages': messages
    })


@app.route('/api/clear-messages', methods=['POST'])
def clear_messages():
    """Limpia los mensajes recibidos"""
    messages.clear()
    return jsonify({
        'success': True,
        'message': 'Mensajes eliminados'
    })


@app.route('/api/get-ip-addresses', methods=['GET'])
def get_ip_addresses():
    """Obtiene todas las direcciones IP disponibles"""
    try:
        ip_addresses = get_all_ip_addresses()
        return jsonify({
            'success': True,
            'ip_addresses': ip_addresses,
            'hostname': socket.gethostname()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Intentar cargar claves existentes
    if os.path.exists('private_key.pem'):
        try:
            crypto_manager.load_keys()
            print("✓ Claves cargadas desde archivos existentes")
        except:
            print("⚠ No se pudieron cargar las claves existentes")

    print(f"\n{'='*60}")
    print(f"  🔐 Aplicación de Mensajería Cifrada RSA")
    print(f"{'='*60}")
    print(f"\n📍 Direcciones IP disponibles para compartir:\n")

    # Obtener y mostrar todas las IPs
    ip_addresses = get_all_ip_addresses()
    if ip_addresses:
        for idx, addr_info in enumerate(ip_addresses, 1):
            print(f"  {idx}. {addr_info['ip']:<15} - {addr_info['type']}")
    else:
        print("  ⚠ No se detectaron direcciones IP")

    print(f"\n{'='*60}")
    print(f"🌐 Acceso Local:  http://localhost:{PORT}")
    print(f"🌐 Acceso Remoto: Usa cualquiera de las IPs mostradas arriba")
    print(f"                  Ejemplo: http://[IP]:{PORT}")
    print(f"{'='*60}")
    print(f"\n💡 Consejo ZeroTier:")
    print(f"   Si usas ZeroTier, comparte la IP que empieza con 10.x.x.x")
    print(f"   Esta IP funcionará desde cualquier dispositivo en tu red ZeroTier")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=PORT, debug=True)
