from ldap3 import Server, Connection, ALL, SUBTREE
import sys

server = Server('******', get_info=ALL, use_ssl=False, port=389, connect_timeout=10)

print("=== Test: Anonymous bind ===")
try:
    conn = Connection(server, auto_bind=True)
    print(f"Anonymous bind: SUCCESS")
    conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', attributes=['sAMAccountName'], size_limit=5)
    print(f"Users found: {len(conn.entries)}")
    for e in conn.entries:
        print(f"  {e.sAMAccountName}")
    conn.unbind()
except Exception as ex:
    print(f"Anonymous bind FAILED: {ex}")

print("\n=== Test: Anonymous search on Root DSE ===")
try:
    conn2 = Connection(server, auto_bind=True)
    conn2.search('', '(objectClass=*)', attributes=['supportedSASLMechanisms', 'supportedLDAPVersion'], search_scope='BASE')
    print(f"Root DSE: {conn2.entries}")
    conn2.unbind()
except Exception as ex:
    print(f"Root DSE search FAILED: {ex}")