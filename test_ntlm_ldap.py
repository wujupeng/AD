import sys
sys.path.insert(0, '/home/debian/AD/backend')
from ldap3 import Server, Connection, ALL, NTLM

server = Server('******', get_info=ALL, use_ssl=False, port=389)
try:
    conn = Connection(server, user='cii.sh.cn\\Administrator', password='YourPassword1!', authentication=NTLM, auto_bind=True)
    print("NTLM bind SUCCESS")
    print("Server info:", server.info.other.get('defaultNamingContext', ['N/A'])[0] if server.info else 'N/A')
    
    conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', attributes=['sAMAccountName','displayName','distinguishedName'], size_limit=50)
    print(f"\nUsers found: {len(conn.entries)}")
    for e in conn.entries[:10]:
        print(f"  {e.sAMAccountName}: {e.displayName} ({e.distinguishedName})")
    
    conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=group)', attributes=['sAMAccountName','distinguishedName'], size_limit=50)
    print(f"\nGroups found: {len(conn.entries)}")
    for e in conn.entries[:10]:
        print(f"  {e.sAMAccountName}: {e.distinguishedName}")
    
    conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=organizationalUnit)', attributes=['name','distinguishedName'], size_limit=50)
    print(f"\nOUs found: {len(conn.entries)}")
    for e in conn.entries[:10]:
        print(f"  {e.name}: {e.distinguishedName}")
    
    conn.unbind()
except Exception as ex:
    print(f"NTLM bind FAILED: {ex}")