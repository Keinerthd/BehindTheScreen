import socket
import threading
import json
import time

PORT = 5555

class NetworkManager:
    def __init__(self):
        self.is_server = False
        self.is_client = False
        self.socket = None
        self.conn = None
        self.addr = None
        self.connected = False
        self.message_queue = []
        self.thread = None
        self.running = False
        
    def host_game(self):
        self.is_server = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Obtener IP local
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = '0.0.0.0'
            
        print(f"[SERVER] Intentando alojar en {local_ip}:{PORT}")
        
        try:
            self.socket.bind(('0.0.0.0', PORT))
            self.socket.listen(1)
            print(f"[SERVER] Esperando conexiones...")
            
            self.running = True
            self.thread = threading.Thread(target=self._server_loop)
            self.thread.daemon = True
            self.thread.start()
            return True, local_ip
        except Exception as e:
            print(f"[SERVER] Error al alojar: {e}")
            return False, str(e)
            
    def join_game(self, ip):
        self.is_client = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[CLIENT] Intentando conectar a {ip}:{PORT}")
        
        try:
            self.socket.connect((ip, PORT))
            self.connected = True
            print("[CLIENT] Conectado exitosamente")
            
            self.running = True
            self.thread = threading.Thread(target=self._client_loop)
            self.thread.daemon = True
            self.thread.start()
            return True, "Conectado"
        except Exception as e:
            print(f"[CLIENT] Error al conectar: {e}")
            return False, str(e)
            
    def _server_loop(self):
        self.socket.settimeout(1.0)
        while self.running and not self.connected:
            try:
                conn, addr = self.socket.accept()
                self.conn = conn
                self.addr = addr
                self.connected = True
                print(f"[SERVER] Cliente conectado desde {addr}")
            except socket.timeout:
                pass
            except Exception as e:
                if self.running:
                    print(f"[SERVER] Error aceptando conexion: {e}")
                
        if self.connected:
            self._receive_loop(self.conn)

    def _client_loop(self):
        self._receive_loop(self.socket)

    def _receive_loop(self, connection):
        connection.settimeout(1.0)
        buffer = ""
        while self.running and self.connected:
            try:
                data = connection.recv(4096).decode('utf-8')
                if not data:
                    print("[NETWORK] Conexion cerrada por el otro lado")
                    self.connected = False
                    break
                    
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        msg = json.loads(line)
                        self.message_queue.append(msg)
                    except json.JSONDecodeError:
                        print(f"[NETWORK] Error decodificando JSON: {line}")
                        
            except socket.timeout:
                pass
            except ConnectionResetError:
                print("[NETWORK] Conexion reseteada")
                self.connected = False
                break
            except Exception as e:
                if self.running:
                    print(f"[NETWORK] Error recibiendo: {e}")

    def send_message(self, message_dict):
        if not self.connected:
            return False
            
        try:
            data = json.dumps(message_dict) + '\n'
            target = self.conn if self.is_server else self.socket
            target.sendall(data.encode('utf-8'))
            return True
        except Exception as e:
            print(f"[NETWORK] Error enviando: {e}")
            self.connected = False
            return False

    def get_messages(self):
        msgs = list(self.message_queue)
        self.message_queue.clear()
        return msgs

    def stop(self):
        self.running = False
        self.connected = False
        if self.conn:
            try: self.conn.close()
            except: pass
        if self.socket:
            try: self.socket.close()
            except: pass
