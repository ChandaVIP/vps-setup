#!/usr/bin/env python3
import socket, threading, select

LISTEN_PORT = 8888
SSH_ADDR = '127.0.0.1'
SSH_PORT = 22

def handle_client(client_socket):
    try:
        client_socket.settimeout(10)
        request = client_socket.recv(8192)
        if not request:
            client_socket.close()
            return

        ssh_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssh_socket.connect((SSH_ADDR, SSH_PORT))

        # ផ្ញើការឆ្លើយតបបញ្ជាក់ការតភ្ជាប់ WebSocket ត្រឹមត្រូវតាមស្ដង់ដារ
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n\r\n"
        )
        client_socket.sendall(response.encode())
        client_socket.settimeout(None)

        def forward(src, dst):
            try:
                while True:
                    r, _, _ = select.select([src], [], [], 60)
                    if not r:
                        break
                    data = src.recv(8192)
                    if not data:
                        break
                    dst.sendall(data)
            except:
                pass
            finally:
                try: src.close()
                except: pass
                try: dst.close()
                except: pass

        threading.Thread(target=forward, args=(client_socket, ssh_socket), daemon=True).start()
        threading.Thread(target=forward, args=(ssh_socket, client_socket), daemon=True).start()
    except:
        try: client_socket.close()
        except: pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(200)
    print(f"ws-proxy listening on 0.0.0.0:{LISTEN_PORT} -> forwarding to {SSH_ADDR}:{SSH_PORT}")

    while True:
        client_sock, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == '__main__':
    main()
