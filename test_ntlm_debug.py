from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import sys

server = Server('******', get_info=ALL, use_ssl=False, port=389, connect_timeout=10)

print("=== Test: NTLM non-auto-bind ===")
conn = Connection(server, user='cii.sh.cn\\Administrator', password='*****',
                  authentication=NTLM, auto_bind=False)
print(f"Connection created, opening...")
conn.open()
print(f"Socket open: {conn.socket is not None}")
result = conn.bind()
print(f"Bind result: {result}")
print(f"Result: {conn.result}")
if result:
    conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', 
                attributes=['sAMAccountName'], size_limit=5)
    print(f"Users: {len(conn.entries)}")
    conn.unbind()
    sys.exit(0)

print("\n=== Test: Try with raise_exceptions=False ===")
conn2 = Connection(server, user='cii.sh.cn\\Administrator', password='*****',
                   authentication=NTLM, auto_bind=False, raise_exceptions=False)
conn2.open()
result2 = conn2.bind()
print(f"Bind result: {result2}")
print(f"Result: {conn2.result}")

print("\n=== Test: Check server info ===")
server_info = Server('******', get_info=ALL, use_ssl=False, port=389)
conn3 = Connection(server_info, user='cii.sh.cn\\Administrator', password='*****',
                   authentication=NTLM, auto_bind=False)
conn3.open()
conn3.bind()
print(f"Server info: {server_info.info}")