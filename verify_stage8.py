import json, subprocess

def api_get(path):
    r = subprocess.run(['curl', '-sk', f'http://127.0.0.1:8000{path}'], capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)

def api_post(path, body):
    r = subprocess.run(['curl', '-sk', '-X', 'POST', f'http://127.0.0.1:8000{path}',
        '-H', 'Content-Type: application/json', '-d', json.dumps(body)],
        capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)

print("=== V01: HTTPS 200 ===")
r = subprocess.run(['curl', '-sk', '-o', '/dev/null', '-w', '%{http_code}', 'https://127.0.0.1/'], capture_output=True, text=True, timeout=10)
print(f"  HTTPS status: {r.stdout}")

print("\n=== V02: DC Registry (all) ===")
dc = api_get('/api/v1/enterprise/dc')
print(f"  Total DCs: {len(dc.get('data', []))}")
for d in dc.get('data', []):
    print(f"    {d['dc_hostname']} ({d['dc_ip_address']}) - {d['dc_site']} - {d['health_status']}")

print("\n=== V03: Cluster Test DFS Shares ===")
shares = api_get('/api/dfs/shares?site_code=cluster_test')
print(f"  Shares: {len(shares.get('data', []))}")
for s in shares.get('data', []):
    print(f"    {s['name']} ({s['type']})")

print("\n=== V04: Cluster Test DFS Files ===")
files = api_get('/api/dfs/files?path=\\\\******\\C$&site_code=cluster_test')
print(f"  Items: {len(files.get('data', {}).get('items', []))}")
for f in files.get('data', {}).get('items', [])[:5]:
    print(f"    {f['name']} ({f['type']})")

print("\n=== V05: CII Factory Login ===")
login = api_post('/api/auth/login', {"username": "Administrator", "password": "*****"})
print(f"  Login: {'PASS' if login['code'] == 0 else 'FAIL'}")

print("\n=== V06: HQ Login ===")
login2 = api_post('/api/auth/login', {"username": "zhangwei", "password": "*****"})
print(f"  Login: {'PASS' if login2['code'] == 0 else 'FAIL'}")

print("\n=== V07: Health Check ===")
health = api_get('/api/health')
print(f"  Status: {health.get('status', 'ok')}")