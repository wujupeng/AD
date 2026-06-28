from ldap3 import Server, Connection, ALL, SASL, SUBTREE, sasl
import sys

server = Server('******', get_info=ALL, use_ssl=False, port=389, connect_timeout=10)

print("=== Test: SASL DIGEST-MD5 ===")
try:
    sasl_creds = sasl.sasl_digest_md5('Administrator', '*****', 'cii.sh.cn')
    conn = Connection(server, user='Administrator', password='*****',
                      authentication=SASL, sasl_mechanism='DIGEST-MD5',
                      sasl_credentials=sasl_creds,
                      auto_bind=False, raise_exceptions=True)
    conn.open()
    result = conn.bind()
    print(f"SASL DIGEST-MD5 bind result: {result}")
    if result:
        conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)',
                    attributes=['sAMAccountName'], size_limit=5)
        print(f"Users: {len(conn.entries)}")
        conn.unbind()
        sys.exit(0)
except Exception as ex:
    print(f"SASL DIGEST-MD5 failed: {ex}")

print("\n=== Test: Direct SASL credentials ===")
try:
    conn2 = Connection(server, sasl_mechanism='DIGEST-MD5',
                       user='Administrator', password='*****',
                       auto_bind=True, raise_exceptions=True)
    print("Direct SASL bind success!")
    conn2.unbind()
except Exception as ex:
    print(f"Direct SASL failed: {ex}")