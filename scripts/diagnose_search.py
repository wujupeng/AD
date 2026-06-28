import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Search for 7777
    r1 = c.get(f"{base}/org/users?page=1&page_size=50&search=7777", headers=headers)
    print(f"Search 7777: status={r1.status_code}")
    print(json.dumps(r1.json(), indent=2)[:500])

    # 2. All users with large page
    r2 = c.get(f"{base}/org/users?page=1&page_size=100", headers=headers)
    d2 = r2.json()
    users = d2.get("data", {}).get("items", [])
    total = d2.get("data", {}).get("total", 0)
    print(f"\nAll users: total={total}, returned={len(users)}")
    for u in users:
        print(f"  {u.get('username', u.get('sam_account_name','?'))} | site={u.get('site_code','?')}")

    # 3. Check DB directly for 7777