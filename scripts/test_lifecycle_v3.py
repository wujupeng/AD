import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Offboard 2009 (liangyinlong)
    print("=== 1. Offboard 2009 ===")
    r1 = c.post(f"{base}/v1/enterprise/identity/offboarding", json={"ad_account": "2009", "offboarding_date": "2026-06-26T00:00:00", "mailbox_retention_days": 0, "wipe_device": True, "revoke_all_access": True}, headers=headers)
    print(f"Status: {r1.status_code}")
    print(json.dumps(r1.json(), indent=2)[:400])

    # 2. Onboard 2030 (李鹏飞)
    print("\n=== 2. Onboard 2030 ===")
    r2 = c.post(f"{base}/v1/enterprise/identity/onboarding", json={"employee_name": "李鹏飞", "sam_account_name": "2030", "department": "gc", "position": "采购员", "site": "cii_factory"}, headers=headers)
    print(f"Status: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2)[:400])

    # 3. Check lifecycle events
    print("\n=== 3. Lifecycle events ===")
    r3 = c.get(f"{base}/v1/enterprise/identity/lifecycle-events?limit=20", headers=headers)
    d3 = r3.json().get("data", [])
    print(f"Total events: {len(d3)}")
    onboarding = [e for e in d3 if e.get("event_type","").startswith("onboarding")]
    offboarding = [e for e in d3 if e.get("event_type","").startswith("offboarding")]
    print(f"Onboarding events: {len(onboarding)}")
    print(f"Offboarding events: {len(offboarding)}")
    for e in d3[:5]:
        print(f"  {e['event_type']} | {e['ad_account']} | {e.get('trigger_source','')}")

    # 4. Check 2009 user status in DB
    print("\n=== 4. Check 2009 user ===")
    r4 = c.get(f"{base}/org/users?search=2009", headers=headers)
    d4 = r4.json().get("data", {}).get("items", [])
    for u in d4:
        if u.get("username") == "2009":
            print(f"  2009 enabled={u.get('is_enabled')}")

    # 5. Check 2030 user in DB
    print("\n=== 5. Check 2030 user ===")
    r5 = c.get(f"{base}/org/users?search=2030", headers=headers)
    d5 = r5.json().get("data", {}).get("items", [])
    for u in d5:
        if u.get("username") == "2030":
            print(f"  2030 found: {u.get('display_name')} enabled={u.get('is_enabled')}")
    if not any(u.get("username") == "2030" for u in d5):
        print("  2030 not found in DB (may need sync)")