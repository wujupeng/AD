import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    if not token:
        print("Login failed")
        exit(1)
    print(f"Login OK")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Org users
    print("\n=== 1. /api/org/users ===")
    r1 = c.get(f"{base}/org/users?page=1&page_size=5", headers=headers)
    print(f"Status: {r1.status_code}")
    d1 = r1.json()
    if r1.status_code == 200 and d1.get("data"):
        users = d1["data"] if isinstance(d1["data"], list) else d1["data"].get("items", d1["data"].get("users", []))
        print(f"Users count: {len(users) if isinstance(users, list) else 'N/A'}")
    else:
        print(json.dumps(d1, indent=2)[:400])

    # 2. OU tree
    print("\n=== 2. /api/org/ou-tree ===")
    r2 = c.get(f"{base}/org/ou-tree", headers=headers)
    print(f"Status: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2)[:500])

    # 3. DFS shares (no site_code)
    print("\n=== 3. /api/dfs/shares (no site) ===")
    r3 = c.get(f"{base}/dfs/shares", headers=headers)
    print(f"Status: {r3.status_code}")
    d3 = r3.json()
    shares = d3.get("data", [])
    print(f"Shares: {len(shares)} - {[s['name'] for s in shares]}")

    # 4. DC management
    print("\n=== 4. /api/v1/enterprise/dc ===")
    r4 = c.get(f"{base}/v1/enterprise/dc", headers=headers)
    dcs = r4.json().get("data", [])
    for dc in dcs:
        if dc["dc_ip_address"].startswith("192.168"):
            print(f"  {dc['dc_hostname']} | {dc['dc_site']} | {dc['dc_ip_address']} | GC={dc['is_gc']}")

    # 5. Audit logs
    print("\n=== 5. /api/audit/logs ===")
    r5 = c.get(f"{base}/audit/logs?page=1&page_size=5", headers=headers)
    print(f"Status: {r5.status_code}")
    print(json.dumps(r5.json(), indent=2)[:500])

    # 6. FSMO roles
    print("\n=== 6. /api/v1/enterprise/dc/fsmo-roles ===")
    r6 = c.get(f"{base}/v1/enterprise/dc/fsmo-roles", headers=headers)
    print(f"Status: {r6.status_code}")
    print(json.dumps(r6.json(), indent=2)[:500])
