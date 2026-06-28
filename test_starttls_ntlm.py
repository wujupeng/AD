from ldap3 import Server, Connection, ALL, NTLM, SUBTREE, Tls
import ssl
import sys

tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT, 
          ca_certs_file=None)
server = Server('******', get_info=ALL, use_ssl=False, port=389, 
                tls=tls, connect_timeout=10)

print("=== Test: StartTLS + NTLM ===")
conn = Connection(server, user='cii.sh.cn\\Administrator', password='*****',
                  authentication=NTLM, auto_bind=False)
conn.open()
print(f"Socket open: {conn.socket is not None}")

print("Starting TLS...")
result = conn.start_tls()
print(f"StartTLS result: {result}")
if result:
    print("TLS established, attempting NTLM bind...")
    bind_result = conn.bind()
    print(f"Bind result: {bind_result}")
    print(f"Result: {conn.result}")
    if bind_result:
        conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)',
                    attributes=['sAMAccountName','displayName','distinguishedName'], size_limit=100)
        print(f"\n=== Users ({len(conn.entries)}) ===")
        for e in conn.entries[:20]:
            sam = str(e.sAMAccountName) if 'sAMAccountName' in e else 'N/A'
            disp = str(e.displayName) if 'displayName' in e else 'N/A'
            dn = str(e.distinguishedName) if 'distinguishedName' in e else 'N/A'
            print(f"  {sam} | {disp} | {dn}")

        conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=group)',
                    attributes=['sAMAccountName','distinguishedName'], size_limit=100)
        print(f"\n=== Groups ({len(conn.entries)}) ===")
        for e in conn.entries[:20]:
            sam = str(e.sAMAccountName) if 'sAMAccountName' in e else 'N/A'
            dn = str(e.distinguishedName) if 'distinguishedName' in e else 'N/A'
            print(f"  {sam} | {dn}")

        conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=organizationalUnit)',
                    attributes=['name','distinguishedName'], size_limit=100)
        print(f"\n=== OUs ({len(conn.entries)}) ===")
        for e in conn.entries:
            name = str(e.name) if 'name' in e else 'N/A'
            dn = str(e.distinguishedName) if 'distinguishedName' in e else 'N/A'
            print(f"  {name} | {dn}")
        
        conn.unbind()
    else:
        print(f"Bind failed: {conn.result}")
else:
    print(f"StartTLS failed: {conn.result}")