import json, subprocess

def api_get(path):
    r = subprocess.run(['curl', '-sk', f'http://127.0.0.1:8000{path}'], capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)

print("=== DFS Shares ===")
shares = api_get('/api/dfs/shares?site_code=cii_factory')
print(f"  Shares: {len(shares.get('data', []))}")
for s in shares.get('data', []):
    print(f"    {s['name']} ({s['type']}) - {s.get('comment', '')}")

print("\n=== DFS Root Files ===")
files = api_get('/api/dfs/files?path=\\\\dcser1\\share&site_code=cii_factory')
print(f"  Items: {len(files.get('data', {}).get('items', []))}")
for f in files.get('data', {}).get('items', []):
    print(f"    {f['name']} ({f['type']}) - {f.get('size', 0)}")

print("\n=== DFS HR Subdir ===")
hr = api_get('/api/dfs/files?path=\\\\dcser1\\share\\HR&site_code=cii_factory')
print(f"  Items: {len(hr.get('data', {}).get('items', []))}")
for f in hr.get('data', {}).get('items', []):
    print(f"    {f['name']} ({f['type']}) - {f.get('size', 0)}")

print("\n=== CII Users ===")
users = api_get('/api/org/users?site_code=cii_factory')
print(f"  Total: {users.get('data', {}).get('total', 0)}")

print("\n=== DC Registry ===")
dc = api_get('/api/v1/enterprise/dc')
cii = [d for d in dc.get('data', []) if d.get('dc_site') == 'cii_factory']
print(f"  CII Factory DCs: {len(cii)}")
for d in cii:
    print(f"    {d['dc_hostname']} ({d['dc_ip_address']}) - {d['health_status']}")