#!/usr/bin/env python3
import ldap3
import ssl

tls = ldap3.Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)
server = ldap3.Server('******', port=636, use_ssl=True, tls=tls, get_info=ldap3.ALL, connect_timeout=10)

try:
    conn = ldap3.Connection(server, user='9999@cii.sh.cn', password='1111', auto_bind=True)
    print('LDAPS simple bind OK')
except Exception as e:
    print(f'LDAPS bind failed: {e}')
    print('Trying LDAP port 389 with SASL...')
    server2 = ldap3.Server('******', port=389, get_info=ldap3.ALL, connect_timeout=5)
    try:
        conn = ldap3.Connection(server2, user='9999@cii.sh.cn', password='1111', auto_bind=True)
        print('LDAP simple bind OK')
    except Exception as e2:
        print(f'LDAP bind also failed: {e2}')
        print('Falling back to anonymous...')
        conn = ldap3.Connection(server2, auto_bind=True)
        print('Anonymous bind OK (limited access)')

naming_ctx = conn.server.info.other.get('defaultNamingContext', ['?'])[0]
print(f'NamingContext: {naming_ctx}')

root_dn = naming_ctx
conn.search(root_dn, '(objectClass=organizationalUnit)', attributes=['ou', 'distinguishedName'], size_limit=30)
print(f'\nOUs ({len(conn.entries)}):')
for entry in conn.entries:
    print(f'  {entry.distinguishedName}')

conn.search(root_dn, '(objectClass=user)', attributes=['sAMAccountName', 'distinguishedName', 'displayName'], size_limit=50)
print(f'\nUsers ({len(conn.entries)}):')
for entry in conn.entries:
    sam = entry.sAMAccountName.value if entry.sAMAccountName else '?'
    dn = entry.distinguishedName.value if entry.distinguishedName else '?'
    disp = entry.displayName.value if entry.displayName else ''
    print(f'  {sam} - {disp} ({dn})')

conn.search(root_dn, '(objectClass=group)', attributes=['cn', 'distinguishedName'], size_limit=50)
print(f'\nGroups ({len(conn.entries)}):')
for entry in conn.entries:
    cn = entry.cn.value if entry.cn else '?'
    dn = entry.distinguishedName.value if entry.distinguishedName else '?'
    print(f'  {cn} ({dn})')

conn.unbind()
print('\nDone!')
