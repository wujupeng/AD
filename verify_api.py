import json, subprocess

def api_get(path):
    r = subprocess.run(['curl', '-sk', f'http://127.0.0.1:8000{path}'], capture_output=True, text=True, timeout=10)
    return json.loads(r.stdout)

users_cii = api_get('/api/org/users?site_code=cii_factory')
print(f"CII Factory Users: {users_cii['data']['total']}")

users_hq = api_get('/api/org/users?site_code=hq')
print(f"HQ Users: {users_hq['data']['total']}")

groups = api_get('/api/org/groups')
print(f"Total Groups: {groups['data']['total']}")

ous = api_get('/api/org/ou-tree')
print(f"Total OUs: {len(ous['data'])}")

dc = api_get('/api/v1/enterprise/dc')
cii_dc = [d for d in dc['data'] if d['dc_site'] == 'cii_factory']
print(f"CII Factory DCs: {len(cii_dc)}")
for d in cii_dc:
    print(f"  {d['dc_hostname']} ({d['dc_ip_address']}) - {d['health_status']}")

health = api_get('/api/health')
print(f"Backend Health: {health.get('status', 'unknown')}")