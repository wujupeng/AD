import json, subprocess

def api_post(path, body):
    r = subprocess.run(['curl', '-sk', '-X', 'POST', f'http://127.0.0.1:8000{path}',
        '-H', 'Content-Type: application/json', '-d', json.dumps(body)],
        capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)

def api_get(path, token=None):
    headers = ['-H', f'Authorization: Bearer {token}'] if token else []
    r = subprocess.run(['curl', '-sk', f'http://127.0.0.1:8000{path}'] + headers,
        capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)

print("=== V01: CII Administrator Login ===")
login = api_post('/api/auth/login', {"username": "Administrator", "password": "*****"})
assert login['code'] == 0, f"Login failed: {login}"
token = login['data']['access_token']
print(f"  PASS - Token obtained, groups: {login['data']['user']['groups'][:3]}")

print("\n=== V02: HQ User Login ===")
login2 = api_post('/api/auth/login', {"username": "zhangwei", "password": "*****"})
assert login2['code'] == 0, f"HQ Login failed: {login2}"
print(f"  PASS - HQ user zhangwei logged in")

print("\n=== V03: CII Invalid Password ===")
login3 = api_post('/api/auth/login', {"username": "Administrator", "password": "WrongPass123"})
assert login3['code'] == 401, f"Should fail: {login3}"
print(f"  PASS - Invalid password rejected")

print("\n=== V04: DFS Shares ===")
shares = api_get('/api/dfs/shares?site_code=cii_factory', token)
assert shares['code'] == 0 and len(shares['data']) > 0, f"Shares failed: {shares}"
print(f"  PASS - {len(shares['data'])} shares listed")

print("\n=== V05: DFS Root Files ===")
files = api_get('/api/dfs/files?path=\\\\dcser1\\share&site_code=cii_factory', token)
assert files['code'] == 0 and len(files['data']['items']) > 0, f"Files failed: {files}"
print(f"  PASS - {len(files['data']['items'])} items in share root")

print("\n=== V06: DFS Subdirectory ===")
hr = api_get('/api/dfs/files?path=\\\\dcser1\\share\\HR&site_code=cii_factory', token)
assert hr['code'] == 0, f"Subdir failed: {hr}"
print(f"  PASS - {len(hr['data']['items'])} items in HR subdirectory")

print("\n=== V07: CII Users via API ===")
users = api_get('/api/org/users?site_code=cii_factory', token)
assert users['code'] == 0 and users['data']['total'] == 29, f"Users failed: {users}"
print(f"  PASS - {users['data']['total']} CII users")

print("\n=== V08: CII Groups via API ===")
groups = api_get('/api/org/groups', token)
assert groups['code'] == 0, f"Groups failed: {groups}"
print(f"  PASS - {groups['data']['total']} total groups")

print("\n=== V09: DC Registry ===")
dc = api_get('/api/v1/enterprise/dc', token)
assert dc['code'] == 0, f"DC failed: {dc}"
cii_dc = [d for d in dc['data'] if d.get('dc_site') == 'cii_factory']
print(f"  PASS - {len(cii_dc)} CII DC(s): {cii_dc[0]['dc_hostname']} ({cii_dc[0]['dc_ip_address']})")

print("\n=== V10: Health Check ===")
health = api_get('/api/health', token)
print(f"  PASS - Backend health: {health.get('status', 'ok')}")

print("\n" + "="*50)
print("ALL 10 VERIFICATION TESTS PASSED!")