#!/usr/bin/env python3
import socket, threading, ssl

LISTEN_PORT = 80
SSH_ADDR = '127.0.0.1'
SSH_PORT = 22

CERT_FILE = '/etc/letsencrypt/live/chanda-vpn.duckdns.org/fullchain.pem'
KEY_FILE = '/etc/letsencrypt/live/chanda-vpn.duckdns.org/privkey.pem'

def handle_client(client_socket):
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        secure_socket = context.wrap_socket(client_socket, server_side=True)

        request = secure_socket.recv(4096)
        if not request:
            secure_socket.close()
            return

        ssh_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssh_socket.connect((SSH_ADDR, SSH_PORT))

        secure_socket.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n")

        def forward(src, dst):
            try:
                while True:
                    data = src.recv(4096)
                    if not data: break
                    dst.sendall(data)
            except:
                pass
            finally:
                try: src.close()
                except: pass
                try: dst.close()
                except: pass

        threading.Thread(target=forward, args=(secure_socket, ssh_socket)).start()
        threading.Thread(target=forward, args=(ssh_socket, secure_socket)).start()
    except:
        try: client_socket.close()
        except: pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(100)
    
    while True:
        client_sock, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == '__main__':
    main()
