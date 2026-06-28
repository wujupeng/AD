import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Offboard 2009 again (should update DB this time)
    print("=== 1. Offboard 2009 ===")
    r1 = c.post(f"{base}/v1/enterprise/identity/offboarding", json={"ad_account": "2009", "offboarding_date": "2026-06-26T00:00:00", "mailbox_retention_days": 0, "wipe_device": True, "revoke_all_access": True}, headers=headers)
    d1 = r1.json().get("data", {})
    print(f"  status={d1.get('status')} step_results={d1.get('step_results')}")

    # 2. Check 2009 in DB
    print("\n=== 2. Check 2009 in DB ===")
    r2 = c.get(f"{base}/org/users?search=2009", headers=headers)
    d2 = r2.json().get("data", {}).get("items", [])
    for u in d2:
        if u.get("username") == "2009":
            print(f"  2009 enabled={u.get('is_enabled')}")

    # 3. Lifecycle events count
    print("\n=== 3. Lifecycle events ===")
    r3 = c.get(f"{base}/v1/enterprise/identity/lifecycle-events?limit=100", headers=headers)
    d3 = r3.json().get("data", [])
    onboarding = [e for e in d3 if e.get("event_type","").startswith("onboarding")]
    offboarding = [e for e in d3 if e.get("event_type","").startswith("offboarding")]
    print(f"Onboarding: {len(onboarding)}, Offboarding: {len(offboarding)}")
    for e in d3[-3:]:
        print(f"  {e['event_type']} | {e['ad_account']}")