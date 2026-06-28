from ldap3 import Server, Connection, ALL, SASL, SUBTREE
import sys

server = Server('******', get_info=ALL, use_ssl=False, port=389, connect_timeout=10)

print("=== Test: SASL DIGEST-MD5 ===")
try:
    conn = Connection(server, sasl_mechanism='DIGEST-MD5',
                      user='Administrator@cii.sh.cn', password='*****',
                      auto_bind=True, raise_exceptions=True)
    print("SASL DIGEST-MD5 bind success!")
    conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)',
                attributes=['sAMAccountName'], size_limit=5)
    print(f"Users: {len(conn.entries)}")
    conn.unbind()
    sys.exit(0)
except Exception as ex:
    print(f"SASL DIGEST-MD5 failed: {ex}")

print("\n=== Test: SASL DIGEST-MD5 with domain\\user ===")
try:
    conn2 = Connection(server, sasl_mechanism='DIGEST-MD5',
                       user='cii.sh.cn\\Administrator', password='*****',
                       auto_bind=True, raise_exceptions=True)
    print("SASL DIGEST-MD5 (domain\\user) bind success!")
    conn2.unbind()
except Exception as ex:
    print(f"SASL DIGEST-MD5 (domain\\user) failed: {ex}")