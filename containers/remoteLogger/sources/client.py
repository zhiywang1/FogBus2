import socket
import ssl

def create_tls_client(server_hostname, port=8443):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((server_hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=server_hostname) as ssock:
                print(f"Connected to {server_hostname} on port {port}")
                ssock.sendall(b"Hello, TLS Server!")
                data = ssock.recv(1024)
                print(f"Received data: {data.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_tls_client('localhost')

