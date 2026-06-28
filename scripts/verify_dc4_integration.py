import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    # Login as Administrator
    r = c.post(f"{base}/auth/login", json={"username": "Administrator", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    if not token:
        print(f"Login failed: {d}")
        exit(1)
    print("V01: CII Administrator login - PASS")
    headers = {"Authorization": f"Bearer {token}"}

    # Test DFS shares for cii_factory_dc4
    r2 = c.get(f"{base}/dfs/shares?site_code=cii_factory_dc4", headers=headers)
    shares = r2.json().get("data", [])
    print(f"V02: DFS shares cii_factory_dc4 - {len(shares)} shares ({', '.join(s['name'] for s in shares)})")

    # Test DFS shares for cii_factory
    r3 = c.get(f"{base}/dfs/shares?site_code=cii_factory", headers=headers)
    shares3 = r3.json().get("data", [])
    print(f"V03: DFS shares cii_factory - {len(shares3)} shares")

    # Test DFS files for cii_factory_dc4 (C$ root)
    r4 = c.get(f"{base}/dfs/files?path=\\\\dc4\\C$&site_code=cii_factory_dc4", headers=headers)
    print(f"V04: DFS files cii_factory_dc4 C$ - Status: {r4.status_code}")
    if r4.status_code == 200:
        files = r4.json().get("data", {}).get("entries", [])
        print(f"     Files: {len(files)} ({', '.join(f.get('name','?') for f in files[:5])})")
    else:
        print(f"     Response: {r4.text[:200]}")

    # Test DFS files for cii_factory (share)
    r5 = c.get(f"{base}/dfs/files?path=\\\\dcser1\\share&site_code=cii_factory", headers=headers)
    print(f"V05: DFS files cii_factory share - Status: {r5.status_code}")
    if r5.status_code == 200:
        files5 = r5.json().get("data", {}).get("entries", [])
        print(f"     Files: {len(files5)} ({', '.join(f.get('name','?') for f in files5[:5])})")

    # Test DC list
    r6 = c.get(f"{base}/v1/enterprise/dc", headers=headers)
    dcs = r6.json().get("data", [])
    dc4_found = any(dc["dc_hostname"] == "dc4" and dc["dc_site"] == "cii_factory" and dc["is_gc"] for dc in dcs)
    dcser1_found = any(dc["dc_hostname"] == "dcser1" and dc["dc_site"] == "cii_factory" for dc in dcs)
    print(f"V06: DC list - dc4(cii_factory,GC)={dc4_found}, dcser1(cii_factory)={dcser1_found}")

    # Test HQ login
    r7 = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    hq_ok = r7.status_code == 200 and (r7.json().get("data", {}).get("success") or r7.json().get("access_token"))
    print(f"V07: HQ user login (zhangwei) - {'PASS' if hq_ok else 'FAIL'}")

    # Test Health
    r8 = c.get(f"{base}/health/detail")
    h = r8.json().get("data", {})
    print(f"V08: Health - Overall: {h.get('status')}")
    for comp, info in h.get("components", {}).items():
        print(f"     {comp}: {info.get('status')}")

    # Test invalid password
    r9 = c.post(f"{base}/auth/login", json={"username": "Administrator", "password": "wrongpassword"})
    invalid_ok = r9.json().get("data", {}).get("error") == "AUTH_INVALID_CREDENTIALS" or r9.json().get("code") == 401
    print(f"V09: Invalid password rejected - {'PASS' if invalid_ok else 'FAIL'}")

    # Test dc4 LDAP via rpcclient
    import subprocess
    result = subprocess.run(["rpcclient", "-U", "CII/Administrator%*****", "-c", "enumdomusers", "******"],
                          capture_output=True, text=True, timeout=15)
    user_count = result.stdout.count("user:[") if result.returncode == 0 else 0
    print(f"V10: dc4 rpcclient enumdomusers - {user_count} users {'PASS' if user_count > 0 else 'FAIL'}")

    print("\n=== Verification Complete ===")
