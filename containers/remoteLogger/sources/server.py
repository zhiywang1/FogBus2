import socket
import ssl

def create_tls_server(certfile, keyfile, port=8443):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind(('localhost', port))
        sock.listen(5)
        print(f"Listening on port {port}...")

        while True:
            try:
                conn, addr = sock.accept()
                with context.wrap_socket(conn, server_side=True) as ssock:
                    print(f"Connection from {addr}")
                    data = ssock.recv(1024)
                    if data:
                        print(f"Received data: {data.decode('utf-8')}")
                        ssock.sendall(b"Hello, TLS Client!")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                if conn:
                    conn.close()

if __name__ == "__main__":
    create_tls_server('server.crt', 'server.key')

