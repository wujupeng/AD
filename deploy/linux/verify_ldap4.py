import ldap3
import socket

# Check DNS resolution
for host in ['dc01.company.local', '127.0.0.1', '127.0.1.1']:
    try:
        info = socket.getaddrinfo(host, 636)
        print(f"{host} -> {info[0][4]}")
    except Exception as e:
        print(f"{host} -> FAILED: {e}")

# Test LDAP with dc01.company.local
server = ldap3.Server('dc01.company.local', port=636, use_ssl=True, connect_timeout=10)
try:
    conn = ldap3.Connection(server, user='Administrator@company.local', password='P@ssw0rd2026!', auto_bind=True)
    print("dc01.company.local LDAP bind SUCCESS")
    conn.unbind()
except Exception as e:
    print(f"dc01.company.local LDAP bind FAILED: {e}")

# Test LDAP with 127.0.0.1
server2 = ldap3.Server('127.0.0.1', port=636, use_ssl=True, connect_timeout=10)
try:
    conn2 = ldap3.Connection(server2, user='Administrator@company.local', password='P@ssw0rd2026!', auto_bind=True)
    print("127.0.0.1 LDAP bind SUCCESS")
    conn2.unbind()
except Exception as e:
    print(f"127.0.0.1 LDAP bind FAILED: {e}")