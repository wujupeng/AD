import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    # Login
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    if not token:
        print("Login failed")
        exit(1)
    print("V01: HQ user login - PASS")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Org users
    r1 = c.get(f"{base}/org/users?page=1&page_size=5", headers=headers)
    d1 = r1.json()
    users = d1.get("data", {}).get("items", []) if r1.status_code == 200 else []
    print(f"V02: Org users - {len(users)} users ({'PASS' if users else 'FAIL'})")

    # 2. OU tree
    r2 = c.get(f"{base}/org/ou-tree", headers=headers)
    d2 = r2.json()
    ous = d2.get("data", []) if r2.status_code == 200 else []
    print(f"V03: OU tree - {len(ous)} OUs ({'PASS' if ous else 'FAIL'})")

    # 3. DFS shares
    r3 = c.get(f"{base}/dfs/shares", headers=headers)
    d3 = r3.json()
    shares = d3.get("data", []) if r3.status_code == 200 else []
    print(f"V04: DFS shares - {len(shares)} shares ({'PASS' if shares else 'FAIL'})")

    # 4. DC list
    r4 = c.get(f"{base}/v1/enterprise/dc", headers=headers)
    dcs = r4.json().get("data", [])
    dc4 = next((dc for dc in dcs if dc["dc_ip_address"] == "******"), None)
    if dc4:
        print(f"V05: DC list - dc4={dc4['dc_hostname']}/{dc4['dc_site']}/GC={dc4['is_gc']} ({'PASS' if dc4['dc_hostname']=='dc4' and dc4['dc_site']=='cii_factory' else 'FAIL'})")
    else:
        print("V05: DC list - dc4 not found FAIL")

    # 5. FSMO roles (was 404 due to route ordering)
    r5 = c.get(f"{base}/v1/enterprise/dc/fsmo-roles", headers=headers)
    d5 = r5.json()
    print(f"V06: FSMO roles - status={r5.status_code} code={d5.get('code')} ({'PASS' if r5.status_code==200 and d5.get('code')==0 else 'CHECK'})")
    if d5.get("data"):
        print(f"     FSMO data: {json.dumps(d5['data'])[:200]}")

    # 6. Audit logs (was 500 due to None filter values)
    r6 = c.get(f"{base}/audit/logs?page=1&page_size=5", headers=headers)
    d6 = r6.json()
    print(f"V07: Audit logs - status={r6.status_code} code={d6.get('code')} ({'PASS' if r6.status_code==200 else 'FAIL'})")
    if r6.status_code == 200 and d6.get("data"):
        items = d6["data"].get("items", [])
        total = d6["data"].get("total", 0)
        print(f"     Audit: {total} total, {len(items)} on page")

    # 7. CII login + audit
    r7 = c.post(f"{base}/auth/login", json={"username": "Administrator", "password": "*****"})
    d7 = r7.json()
    cii_ok = d7.get("data", {}).get("success") or d7.get("access_token")
    print(f"V08: CII Administrator login - {'PASS' if cii_ok else 'FAIL'}")

    # 8. Check audit after login
    r8 = c.get(f"{base}/audit/logs?page=1&page_size=5", headers=headers)
    d8 = r8.json()
    if r8.status_code == 200 and d8.get("data"):
        total = d8["data"].get("total", 0)
        print(f"V09: Audit logs after login - {total} records ({'PASS' if total > 0 else 'NEED CHECK'})")
    else:
        print(f"V09: Audit logs after login - FAIL ({r8.status_code})")

    # 9. Health
    r9 = c.get(f"{base}/health/detail")
    h = r9.json().get("data", {})
    print(f"V10: Health - {h.get('status')}")