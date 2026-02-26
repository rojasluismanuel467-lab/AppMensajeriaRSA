from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
import socket
from crypto_utils import CryptoManager

app = Flask(__name__)
CORS(app)
crypto_manager = CryptoManager()

messages = []
PORT = 5000


def get_all_ip_addresses():
    ip_addresses = []
    hostname = socket.gethostname()

    try:
        addrs = socket.getaddrinfo(hostname, None)
        seen = set()

        for addr in addrs:
            ip = addr[4][0]
            if ':' not in ip and not ip.startswith('127.'):
                if ip not in seen:
                    seen.add(ip)

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

    if not ip_addresses:
        try:
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
    return render_template('index.html')


@app.route('/api/generate-keys', methods=['POST'])
def generate_keys():
    try:
        public_key = crypto_manager.generate_keys()
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
    try:
        if crypto_manager.public_key:
            public_key = crypto_manager.get_public_key_string()
        else:
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

        encrypted_message = crypto_manager.encrypt_message(message, recipient_public_key)

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
    try:
        data = request.json
        encrypted_message = data.get('encrypted_message')

        if not encrypted_message:
            return jsonify({
                'success': False,
                'error': 'No se recibió el mensaje'
            }), 400

        if not crypto_manager.private_key:
            if os.path.exists('private_key.pem'):
                crypto_manager.load_keys()
            else:
                return jsonify({
                    'success': False,
                    'error': 'No hay claves para descifrar'
                }), 400

        decrypted_message = crypto_manager.decrypt_message(encrypted_message)

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
    return jsonify({
        'success': True,
        'messages': messages
    })


@app.route('/api/clear-messages', methods=['POST'])
def clear_messages():
    messages.clear()
    return jsonify({
        'success': True,
        'message': 'Mensajes eliminados'
    })


@app.route('/api/get-ip-addresses', methods=['GET'])
def get_ip_addresses():
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
    if os.path.exists('private_key.pem'):
        try:
            crypto_manager.load_keys()
            print("Claves cargadas desde archivos existentes")
        except:
            print("No se pudieron cargar las claves existentes")

    print(f"\n{'='*60}")
    print(f"  Aplicación de Mensajería Cifrada RSA")
    print(f"{'='*60}")
    print(f"\nDirecciones IP disponibles para compartir:\n")

    ip_addresses = get_all_ip_addresses()
    if ip_addresses:
        for idx, addr_info in enumerate(ip_addresses, 1):
            print(f"  {idx}. {addr_info['ip']:<15} - {addr_info['type']}")
    else:
        print("  No se detectaron direcciones IP")

    print(f"\n{'='*60}")
    print(f"Acceso Local:  http://localhost:{PORT}")
    print(f"Acceso Remoto: Usa cualquiera de las IPs mostradas arriba")
    print(f"               Ejemplo: http://[IP]:{PORT}")
    print(f"{'='*60}")
    print(f"\nConsejo ZeroTier:")
    print(f"  Si usas ZeroTier, comparte la IP que empieza con 10.x.x.x")
    print(f"  Esta IP funcionará desde cualquier dispositivo en tu red ZeroTier")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=PORT, debug=True)
