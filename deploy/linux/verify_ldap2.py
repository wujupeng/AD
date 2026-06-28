import ldap3
server = ldap3.Server('dc01.company.local', port=636, use_ssl=True, connect_timeout=10)
try:
    conn = ldap3.Connection(server, user='CN=svc_adbiz,OU=ServiceAccounts,OU=Company,DC=company,DC=local', password='*****', auto_bind=True)
    print("Service account bind SUCCESS")
    conn.search('DC=company,DC=local', '(objectClass=*)', search_scope='BASE', attributes=['dn'])
    for entry in conn.entries:
        print("Base search:", entry.dn)
    conn.unbind()
except Exception as e:
    print(f"Service account bind FAILED: {type(e).__name__}: {e}")

try:
    conn2 = ldap3.Connection(server, user='CN=zhangwei,CN=Users,DC=company,DC=local', password='*****', auto_bind=True)
    print("User zhangwei bind SUCCESS")
    conn2.unbind()
except Exception as e:
    print(f"User zhangwei bind FAILED: {type(e).__name__}: {e}")