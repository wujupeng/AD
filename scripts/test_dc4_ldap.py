import ldap3

# Test 1: Simple bind on port 389
print("=== Test 1: Simple bind on port 389 ===")
try:
    server = ldap3.Server('******', port=389)
    conn = ldap3.Connection(server, user='Administrator@cii.sh.cn', password='*****')
    result = conn.bind()
    print(f"Result: {result}, Description: {conn.result['description']}")
    conn.unbind()
except Exception as ex:
    print(f"Failed: {ex}")

# Test 2: LDAPS on port 636
print("\n=== Test 2: Simple bind on port 636 (LDAPS) ===")
try:
    server2 = ldap3.Server('******', port=636, use_ssl=True)
    conn2 = ldap3.Connection(server2, user='Administrator@cii.sh.cn', password='*****')
    result2 = conn2.bind()
    print(f"Result: {result2}, Description: {conn2.result['description']}")
    if result2:
        conn2.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', attributes=['sAMAccountName'])
        print(f"Total users: {len(conn2.entries)}")
    conn2.unbind()
except Exception as ex:
    print(f"Failed: {ex}")

# Test 3: NTLM on port 389
print("\n=== Test 3: NTLM on port 389 ===")
try:
    server3 = ldap3.Server('******', port=389)
    conn3 = ldap3.Connection(server3, user='cii.sh.cn\\Administrator', password='*****', authentication=ldap3.NTLM)
    result3 = conn3.bind()
    print(f"Result: {result3}, Description: {conn3.result['description']}")
    if result3:
        conn3.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', attributes=['sAMAccountName'])
        print(f"Total users: {len(conn3.entries)}")
        for e in conn3.entries[:5]:
            print(f"  User: {e.sAMAccountName}")
    conn3.unbind()
except Exception as ex:
    print(f"Failed: {ex}")

# Test 4: SASL DIGEST-MD5
print("\n=== Test 4: SASL DIGEST-MD5 on port 389 ===")
try:
    server4 = ldap3.Server('******', port=389)
    conn4 = ldap3.Connection(server4, authentication=ldap3.SASL, sasl_mechanism='DIGEST-MD5',
                              sasl_credentials=(None, 'Administrator', '*****', None))
    result4 = conn4.bind()
    print(f"Result: {result4}, Description: {conn4.result['description']}")
    if result4:
        conn4.search('DC=cii,DC=sh,DC=cn', '(objectClass=user)', attributes=['sAMAccountName'])
        print(f"Total users: {len(conn4.entries)}")
    conn4.unbind()
except Exception as ex:
    print(f"Failed: {ex}")

# Test 5: rpcclient
print("\n=== Test 5: rpcclient on dc4 ===")
import subprocess
r = subprocess.run(['rpcclient', '-U', 'cii.sh.cn/Administrator%*****', '-c', 'enumdomusers', '******'],
                   capture_output=True, text=True, timeout=15)
print(f"rpcclient exit: {r.returncode}")
if r.stdout:
    lines = r.stdout.strip().split('\n')
    print(f"Users via rpcclient: {len(lines)}")
    for l in lines[:5]:
        print(f"  {l}")
if r.stderr:
    print(f"stderr: {r.stderr[:200]}")

# Test 6: net ads search
print("\n=== Test 6: net ads search on dc4 ===")
r2 = subprocess.run(['net', 'ads', 'search', '-U', 'cii.sh.cn/Administrator%*****', '-S', '******',
                     '-P', '(objectClass=user)', 'sAMAccountName'],
                    capture_output=True, text=True, timeout=15)
print(f"net ads exit: {r2.returncode}")
if r2.stdout:
    print(r2.stdout[:500])
if r2.stderr:
    print(f"stderr: {r2.stderr[:200]}")
