import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Search 7777
    r1 = c.get(f"{base}/org/users?page=1&page_size=50&search=7777", headers=headers)
    d1 = r1.json()
    items = d1.get("data", {}).get("items", [])
    total = d1.get("data", {}).get("total", 0)
    print(f"Search '7777': total={total}, items={len(items)}")
    for u in items:
        print(f"  {u['username']} | {u['display_name']} | {u['site_code']}")

    # Search zhang
    r2 = c.get(f"{base}/org/users?page=1&page_size=50&search=zhang", headers=headers)
    d2 = r2.json()
    items2 = d2.get("data", {}).get("items", [])
    total2 = d2.get("data", {}).get("total", 0)
    print(f"\nSearch 'zhang': total={total2}, items={len(items2)}")
    for u in items2:
        print(f"  {u['username']} | {u['display_name']} | {u['site_code']}")

    # Search empty (all)
    r3 = c.get(f"{base}/org/users?page=1&page_size=5", headers=headers)
    d3 = r3.json()
    total3 = d3.get("data", {}).get("total", 0)
    print(f"\nNo search: total={total3}")