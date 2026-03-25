import socket
import sys

def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"Port {port} on {host} is OPEN.")
            return True
    except Exception as e:
        print(f"Port {port} on {host} is CLOSED: {e}")
        return False

if __name__ == "__main__":
    check_port("127.0.0.1", 7687)
