"""
Módulo de red para comunicación LAN.
Permite enviar y recibir mensajes cifrados entre computadoras en la misma red.
"""

import socket
import threading
import json
from pathlib import Path
from typing import Callable, Optional, List, Tuple
import netifaces
from crypto import cifrar_mensaje, descifrar_mensaje
from keys import cargar_clave_privada, cargar_clave_publica, obtener_clave_publica_desde_privada


PUERTO_DEFAULT = 55555
BUFFER_SIZE = 65536


def obtener_todas_las_ips() -> List[Tuple[str, str, str]]:
    """
    Obtiene todas las interfaces de red con sus IPs.

    Returns:
        Lista de tuplas (nombre_interfaz, ip, descripción)
    """
    interfaces = []

    try:
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)

            # Obtener direcciones IPv4
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr.get('addr', '')

                    # Filtrar localhost
                    if ip and ip != '127.0.0.1':
                        # Detectar tipo de interfaz
                        descripcion = ""
                        interface_lower = interface.lower()

                        if 'zerotier' in interface_lower or 'zt' in interface_lower:
                            descripcion = "ZeroTier (VPN)"
                        elif 'ethernet' in interface_lower or 'eth' in interface_lower:
                            descripcion = "Ethernet (Cable)"
                        elif 'wi-fi' in interface_lower or 'wlan' in interface_lower or 'wireless' in interface_lower:
                            descripcion = "WiFi (Inalámbrica)"
                        elif 'vmware' in interface_lower or 'virtualbox' in interface_lower:
                            descripcion = "Máquina Virtual"
                        else:
                            descripcion = "Red Local"

                        interfaces.append((interface, ip, descripcion))
    except Exception as e:
        print(f"Error obteniendo interfaces: {e}")

    return interfaces


def obtener_ip_local() -> str:
    """
    Obtiene la IP local de la máquina.
    Prioriza interfaces físicas sobre virtuales.
    """
    interfaces = obtener_todas_las_ips()

    if not interfaces:
        return "127.0.0.1"

    # Prioridad: WiFi/Ethernet > ZeroTier > Otras
    for nombre, ip, desc in interfaces:
        if "WiFi" in desc or "Ethernet" in desc:
            return ip

    # Si no hay físicas, usar ZeroTier
    for nombre, ip, desc in interfaces:
        if "ZeroTier" in desc:
            return ip

    # Si no, usar la primera disponible
    return interfaces[0][1]


class ServidorMensajeria:
    """Servidor que escucha mensajes entrantes."""
    
    def __init__(self, puerto: int = PUERTO_DEFAULT):
        self.puerto = puerto
        self.socket_servidor: Optional[socket.socket] = None
        self.hilo_servidor: Optional[threading.Thread] = None
        self.ejecutando = False
        self.callback_mensaje: Optional[Callable] = None
        self.callback_estado: Optional[Callable] = None
    
    def iniciar(self, callback_mensaje: Callable, callback_estado: Callable):
        """Inicia el servidor en un hilo separado."""
        self.callback_mensaje = callback_mensaje
        self.callback_estado = callback_estado
        
        try:
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_servidor.bind(('0.0.0.0', self.puerto))
            self.socket_servidor.listen(5)
            self.socket_servidor.settimeout(1.0)
            
            self.ejecutando = True
            self.hilo_servidor = threading.Thread(target=self._aceptar_conexiones, daemon=True)
            self.hilo_servidor.start()
            
            if self.callback_estado:
                self.callback_estado(f"✅ Servidor activo en puerto {self.puerto}")
                
        except Exception as e:
            if self.callback_estado:
                self.callback_estado(f"❌ Error al iniciar servidor: {e}")
    
    def _aceptar_conexiones(self):
        """Acepta conexiones entrantes."""
        while self.ejecutando:
            try:
                cliente, addr = self.socket_servidor.accept()
                hilo = threading.Thread(
                    target=self._manejar_cliente,
                    args=(cliente, addr),
                    daemon=True
                )
                hilo.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.ejecutando and self.callback_estado:
                    self.callback_estado(f"❌ Error aceptando conexión: {e}")
                break
    
    def _manejar_cliente(self, cliente: socket.socket, addr: tuple):
        """Maneja la comunicación con un cliente."""
        try:
            cliente.settimeout(5.0)
            datos = cliente.recv(BUFFER_SIZE)
            
            if datos:
                mensaje = datos.decode('utf-8')
                
                # Parsear mensaje JSON
                try:
                    data = json.loads(mensaje)
                    tipo = data.get('tipo', 'mensaje')
                    contenido = data.get('contenido', '')
                    
                    if tipo == 'mensaje':
                        # Mensaje cifrado recibido
                        if self.callback_mensaje:
                            self.callback_mensaje({
                                'origen': addr[0],
                                'mensaje_cifrado': contenido,
                                'tipo': 'recibido'
                            })
                        
                        if self.callback_estado:
                            self.callback_estado(f"📩 Mensaje recibido de {addr[0]}")
                    
                    elif tipo == 'clave_publica':
                        # Alguien envía su clave pública
                        if self.callback_mensaje:
                            self.callback_mensaje({
                                'origen': addr[0],
                                'clave_publica': contenido,
                                'tipo': 'clave'
                            })
                        
                        if self.callback_estado:
                            self.callback_estado(f"🔑 Clave pública recibida de {addr[0]}")
                            
                except json.JSONDecodeError:
                    # Mensaje no JSON, tratar como texto plano
                    if self.callback_mensaje:
                        self.callback_mensaje({
                            'origen': addr[0],
                            'mensaje': contenido,
                            'tipo': 'texto'
                        })
            
        except Exception as e:
            if self.callback_estado:
                self.callback_estado(f"⚠️ Error con cliente {addr[0]}: {e}")
        finally:
            cliente.close()
    
    def detener(self):
        """Detiene el servidor."""
        self.ejecutando = False
        if self.socket_servidor:
            try:
                self.socket_servidor.close()
            except:
                pass
        if self.callback_estado:
            self.callback_estado("⛔ Servidor detenido")


class ClienteMensajeria:
    """Cliente para enviar mensajes a un servidor."""
    
    def __init__(self):
        self.socket_cliente: Optional[socket.socket] = None
        self.callback_estado: Optional[Callable] = None
    
    def conectar(self, ip: str, puerto: int = PUERTO_DEFAULT, 
                 callback_estado: Optional[Callable] = None) -> bool:
        """Conecta a un servidor remoto."""
        self.callback_estado = callback_estado
        
        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.settimeout(5.0)
            self.socket_cliente.connect((ip, puerto))
            
            if self.callback_estado:
                self.callback_estado(f"✅ Conectado a {ip}:{puerto}")
            return True
            
        except Exception as e:
            if self.callback_estado:
                self.callback_estado(f"❌ Error conectando a {ip}:{puerto} - {e}")
            return False
    
    def enviar_mensaje(self, mensaje_cifrado: str) -> bool:
        """Envía un mensaje cifrado al servidor."""
        if not self.socket_cliente:
            if self.callback_estado:
                self.callback_estado("❌ No hay conexión activa")
            return False
        
        try:
            data = json.dumps({
                'tipo': 'mensaje',
                'contenido': mensaje_cifrado
            }).encode('utf-8')
            
            self.socket_cliente.sendall(data)
            
            if self.callback_estado:
                self.callback_estado("📤 Mensaje enviado")
            return True
            
        except Exception as e:
            if self.callback_estado:
                self.callback_estado(f"❌ Error enviando: {e}")
            return False
    
    def enviar_clave_publica(self, pem_clave_publica: str) -> bool:
        """Envía la clave pública al servidor."""
        if not self.socket_cliente:
            return False
        
        try:
            data = json.dumps({
                'tipo': 'clave_publica',
                'contenido': pem_clave_publica
            }).encode('utf-8')
            
            self.socket_cliente.sendall(data)
            return True
        except:
            return False
    
    def desconectar(self):
        """Desconecta del servidor."""
        if self.socket_cliente:
            try:
                self.socket_cliente.close()
            except:
                pass
            self.socket_cliente = None
        
        if self.callback_estado:
            self.callback_estado("⛔ Desconectado")


class GestorRed:
    """Gestiona servidor y clientes de red."""
    
    def __init__(self):
        self.servidor = ServidorMensajeria()
        self.cliente = ClienteMensajeria()
        self.usuario = None
        self.callback_mensaje: Optional[Callable] = None
        self.callback_estado: Optional[Callable] = None
    
    def configurar(self, usuario: dict, 
                   callback_mensaje: Callable,
                   callback_estado: Callable):
        """Configura el gestor con el usuario actual."""
        self.usuario = usuario
        self.callback_mensaje = callback_mensaje
        self.callback_estado = callback_estado
        
        # Configurar callbacks del servidor
        self.servidor.callback_mensaje = self._manejar_mensaje_entrante
        self.servidor.callback_estado = callback_estado
    
    def _manejar_mensaje_entrante(self, data: dict):
        """Maneja mensajes entrantes del servidor."""
        if data.get('tipo') == 'recibido':
            # Intentar descifrar el mensaje
            try:
                mensaje_cifrado = data.get('mensaje_cifrado', '')
                origen = data.get('origen', 'desconocido')
                
                if self.usuario and self.usuario.get('clave_privada'):
                    mensaje_descifrado = descifrar_mensaje(
                        mensaje_cifrado,
                        self.usuario['clave_privada']
                    )
                    
                    if self.callback_mensaje:
                        self.callback_mensaje({
                            'origen': origen,
                            'mensaje_cifrado': mensaje_cifrado,
                            'mensaje_descifrado': mensaje_descifrado,
                            'tipo': 'recibido_cifrado'
                        })
            except Exception as e:
                if self.callback_estado:
                    self.callback_estado(f"⚠️ No se pudo descifrar: {e}")
        
        elif data.get('tipo') == 'clave':
            # Guardar clave pública recibida
            try:
                origen = data.get('origen', 'desconocido')
                pem_clave = data.get('clave_publica', '')
                
                if pem_clave and origen != 'desconocido':
                    # Guardar clave con nombre de IP
                    from keys import importar_clave_publica_pem, guardar_clave_publica
                    clave_publica = importar_clave_publica_pem(pem_clave)
                    Path("claves").mkdir(exist_ok=True)
                    nombre_archivo = f"claves/{origen}_publica.pem"
                    guardar_clave_publica(clave_publica, nombre_archivo)
                    
                    if self.callback_estado:
                        self.callback_estado(f"💾 Clave de {origen} guardada")
                        
            except Exception as e:
                if self.callback_estado:
                    self.callback_estado(f"⚠️ Error guardando clave: {e}")
    
    def iniciar_servidor(self, puerto: int = PUERTO_DEFAULT):
        """Inicia el servidor de mensajería."""
        self.servidor.iniciar(self._manejar_mensaje_entrante, self.callback_estado)
    
    def detener_servidor(self):
        """Detiene el servidor."""
        self.servidor.detener()
    
    def conectar_a(self, ip: str, puerto: int = PUERTO_DEFAULT) -> bool:
        """Conecta a otro usuario."""
        return self.cliente.conectar(ip, puerto, self.callback_estado)
    
    def enviar_a(self, ip: str, mensaje: str, destinatario_nombre: str = None) -> bool:
        """Envía un mensaje cifrado a una IP."""
        if not self.usuario:
            if self.callback_estado:
                self.callback_estado("❌ No hay usuario cargado")
            return False
        
        try:
            # Cargar clave pública del destinatario
            if destinatario_nombre:
                ruta_publica = f"claves/{destinatario_nombre}_publica.pem"
            else:
                # Usar IP como nombre
                ruta_publica = f"claves/{ip.replace('.', '_')}_publica.pem"
            
            if not Path(ruta_publica).exists():
                if self.callback_estado:
                    self.callback_estado(f"❌ No hay clave pública para {destinatario_nombre or ip}")
                return False
            
            clave_publica = cargar_clave_publica(ruta_publica)
            mensaje_cifrado = cifrar_mensaje(mensaje, clave_publica)
            
            # Conectar y enviar
            if self.cliente.conectar(ip, PUERTO_DEFAULT, self.callback_estado):
                exito = self.cliente.enviar_mensaje(mensaje_cifrado)
                self.cliente.desconectar()
                
                # Guardar mensaje enviado
                if exito:
                    Path("mensajes").mkdir(exist_ok=True)
                    # Use the number of files in 'mensajes' for unique filename
                    mensajes_dir = Path("mensajes")
                    count = len(list(mensajes_dir.glob("para_{}_*".format(ip))))
                    nombre_archivo = f"mensajes/para_{ip}_{count}.txt"
                    try:
                        with open(nombre_archivo, 'w') as f:
                            f.write(mensaje_cifrado)
                    except:
                        pass
                
                return exito
            
            return False
            
        except Exception as e:
            if self.callback_estado:
                self.callback_estado(f"❌ Error: {e}")
            return False
    
    def obtener_ip_local(self) -> str:
        """Obtiene la IP local."""
        return obtener_ip_local()
    
    def cerrar(self):
        """Cierra todas las conexiones."""
        self.servidor.detener()
        self.cliente.desconectar()


# Instancia global para facilitar uso
gestor = GestorRed()
