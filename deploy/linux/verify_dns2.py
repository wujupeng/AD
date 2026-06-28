import socket
for host in ['localhost', '127.0.0.1', 'dc01.company.local']:
    try:
        result = socket.getaddrinfo(host, 5432)
        print(f"{host} -> {result[0][4]}")
    except Exception as e:
        print(f"{host} -> FAILED: {e}")