import ldap3

server = ldap3.Server('dc01.company.local', port=636, use_ssl=True, connect_timeout=10)

# Test service account with DN
try:
    conn = ldap3.Connection(server, user='CN=svc_adbiz,OU=ServiceAccounts,OU=Company,DC=company,DC=local', password='SvcP@ss2026!', auto_bind=True)
    print("svc_adbiz DN bind SUCCESS")
    conn.search('DC=company,DC=local', '(sAMAccountName=zhangwei)', search_scope=ldap3.SUBTREE, attributes=['distinguishedName', 'displayName', 'mail', 'objectSid', 'userAccountControl'])
    for entry in conn.entries:
        print("zhangwei DN:", entry.distinguishedName)
        print("zhangwei attrs:", entry.entry_attributes_as_dict)
    conn.unbind()
except Exception as e:
    print(f"svc_adbiz DN bind FAILED: {type(e).__name__}: {e}")

# Test service account with UPN
try:
    conn2 = ldap3.Connection(server, user='svc_adbiz@company.local', password='SvcP@ss2026!', auto_bind=True)
    print("svc_adbiz UPN bind SUCCESS")
    conn2.unbind()
except Exception as e:
    print(f"svc_adbiz UPN bind FAILED: {type(e).__name__}: {e}")