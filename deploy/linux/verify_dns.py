import socket
try:
    result = socket.getaddrinfo('dc01.company.local', 636)
    print("DNS resolution OK:", result)
except Exception as e:
    print("DNS resolution FAILED:", e)