import ldap3
server = ldap3.Server('ldaps://dc01.company.local', connect_timeout=5)
conn = ldap3.Connection(server, user='CN=Administrator,CN=Users,DC=company,DC=local', password='P@ssw0rd2026!', auto_bind=True)
print('LDAP bind SUCCESS')
conn.search('DC=company,DC=local', '(objectClass=domain)', search_scope='BASE', attributes=['dn'])
for entry in conn.entries:
    print('Found:', entry.dn)
conn.unbind()