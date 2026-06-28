import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Mail/contacts
    print("=== 1. /contacts ===")
    r1 = c.get(f"{base}/contacts", headers=headers)
    print(f"Status: {r1.status_code}")
    print(json.dumps(r1.json(), indent=2)[:300])

    # 2. Mail send
    print("\n=== 2. /mail ===")
    r2 = c.get(f"{base}/mail/send", headers=headers)
    print(f"Status: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2)[:200])

    # 3. LDAP integration configs
    print("\n=== 3. /integration/sp-configs ===")
    r3 = c.get(f"{base}/integration/sp-configs", headers=headers)
    print(f"Status: {r3.status_code}")
    print(json.dumps(r3.json(), indent=2)[:500])

    # 4. Settings LDAP integration
    print("\n=== 4. /v1/enterprise/settings/integrations/ldap ===")
    r4 = c.get(f"{base}/v1/enterprise/settings/integrations/ldap", headers=headers)
    print(f"Status: {r4.status_code}")
    print(json.dumps(r4.json(), indent=2)[:500])

    # 5. DFS-R replication status
    print("\n=== 5. /v1/enterprise/dfs/replication-status ===")
    r5 = c.get(f"{base}/v1/enterprise/dfs/replication-status", headers=headers)
    print(f"Status: {r5.status_code}")
    print(json.dumps(r5.json(), indent=2)[:500])

    # 6. PKI templates
    print("\n=== 6. /v1/enterprise/pki/templates ===")
    r6 = c.get(f"{base}/v1/enterprise/pki/templates", headers=headers)
    print(f"Status: {r6.status_code}")
    print(json.dumps(r6.json(), indent=2)[:500])

    # 7. PKI expiring
    print("\n=== 7. /v1/enterprise/pki/expiring ===")
    r7 = c.get(f"{base}/v1/enterprise/pki/expiring?days=30", headers=headers)
    print(f"Status: {r7.status_code}")
    print(json.dumps(r7.json(), indent=2)[:500])

    # 8. Site configs
    print("\n=== 8. /v1/enterprise/settings/sites ===")
    r8 = c.get(f"{base}/v1/enterprise/settings/sites", headers=headers)
    print(f"Status: {r8.status_code}")
    print(json.dumps(r8.json(), indent=2)[:500])