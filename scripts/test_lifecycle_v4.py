import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Offboard 2009
    print("=== 1. Offboard 2009 ===")
    r1 = c.post(f"{base}/v1/enterprise/identity/offboarding", json={"ad_account": "2009", "offboarding_date": "2026-06-26T00:00:00", "mailbox_retention_days": 0, "wipe_device": True, "revoke_all_access": True}, headers=headers)
    print(f"Status: {r1.status_code}")
    d1 = r1.json().get("data", {})
    print(f"  status={d1.get('status')} step_results={d1.get('step_results')}")

    # 2. Check lifecycle events count
    print("\n=== 2. Lifecycle events ===")
    r2 = c.get(f"{base}/v1/enterprise/identity/lifecycle-events?limit=100", headers=headers)
    d2 = r2.json().get("data", [])
    onboarding = [e for e in d2 if e.get("event_type","").startswith("onboarding")]
    offboarding = [e for e in d2 if e.get("event_type","").startswith("offboarding")]
    print(f"Onboarding: {len(onboarding)}, Offboarding: {len(offboarding)}")

    # 3. Check 2009 status via rpcclient
    import subprocess
    r3 = subprocess.run(["ssh", "debian@******", "rpcclient -U 'CII/Administrator%*****' -c 'queryuser 2009' ******"], capture_output=True, text=True, timeout=15)
    print(f"\n=== 3. 2009 user status ===")
    for line in r3.stdout.split("\n"):
        if "Account" in line or "Disabled" in line or "Flags" in line:
            print(f"  {line.strip()}")