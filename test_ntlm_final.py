from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import sys

server = Server('******', get_info=ALL, use_ssl=False, port=389, connect_timeout=10)

conn = Connection(server, user='cii.sh.cn\\Administrator', password='*****',
                  authentication=NTLM, auto_bind=True)
print("NTLM bind SUCCESS!")

print("\n=== Users ===")
conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', 
            attributes=['sAMAccountName','displayName','distinguishedName'], size_limit=100)
print(f"Total: {len(conn.entries)}")
for e in conn.entries[:20]:
    sam = str(e.sAMAccountName) if e.sAMAccountName else 'N/A'
    dn = str(e.distinguishedName) if e.distinguishedName else 'N/A'
    disp = str(e.displayName) if e.displayName else 'N/A'
    print(f"  {sam} | {disp} | {dn}")

print("\n=== Groups ===")
conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=group)',
            attributes=['sAMAccountName','distinguishedName'], size_limit=100)
print(f"Total: {len(conn.entries)}")
for e in conn.entries[:20]:
    sam = str(e.sAMAccountName) if e.sAMAccountName else 'N/A'
    dn = str(e.distinguishedName) if e.distinguishedName else 'N/A'
    print(f"  {sam} | {dn}")

print("\n=== OUs ===")
conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=organizationalUnit)',
            attributes=['name','distinguishedName'], size_limit=100)
print(f"Total: {len(conn.entries)}")
for e in conn.entries:
    name = str(e.name) if e.name else 'N/A'
    dn = str(e.distinguishedName) if e.distinguishedName else 'N/A'
    print(f"  {name} | {dn}")

conn.unbind()