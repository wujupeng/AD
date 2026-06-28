import ldap3

server = ldap3.Server('127.0.0.1', port=636, use_ssl=True, connect_timeout=10)

# Test with Administrator
try:
    conn = ldap3.Connection(server, user='Administrator@company.local', password='*****', auto_bind=True)
    print("Administrator UPN bind SUCCESS")
    conn.unbind()
except Exception as e:
    print(f"Administrator UPN bind FAILED: {e}")

# Test with DN format
try:
    conn = ldap3.Connection(server, user='CN=Administrator,CN=Users,DC=company,DC=local', password='*****', auto_bind=True)
    print("Administrator DN bind SUCCESS")
    conn.unbind()
except Exception as e:
    print(f"Administrator DN bind FAILED: {e}")

# Test svc_adbiz
try:
    conn = ldap3.Connection(server, user='svc_adbiz@company.local', password='*****', auto_bind=True)
    print("svc_adbiz UPN bind SUCCESS")
    conn.unbind()
except Exception as e:
    print(f"svc_adbiz UPN bind FAILED: {e}")

# Test zhangwei
try:
    conn = ldap3.Connection(server, user='zhangwei@company.local', password='*****', auto_bind=True)
    print("zhangwei UPN bind SUCCESS")
    conn.unbind()
except Exception as e:
    print(f"zhangwei UPN bind FAILED: {e}")