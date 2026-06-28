import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Site options (dynamic from API)
    print("=== 1. Sites ===")
    r1 = c.get(f"{base}/v1/enterprise/settings/sites", headers=headers)
    sites = r1.json().get("data", [])
    for s in sites:
        print(f"  {s['site_code']}: {s.get('site_display_name') or s.get('site_name')}")

    # 2. Mail contacts
    print("\n=== 2. Contacts ===")
    r2 = c.get(f"{base}/contacts?q=*&limit=5", headers=headers)
    print(f"Status: {r2.status_code}")
    d2 = r2.json()
    items = d2.get("data", [])
    if isinstance(items, list):
        print(f"Contacts: {len(items)}")
        for i in items[:3]:
            print(f"  {i.get('display_name','?')} | {i.get('email','?')} | {i.get('site_code','?')}")
    else:
        print(json.dumps(d2, indent=2)[:300])

    # 3. LDAP directory configs
    print("\n=== 3. LDAP configs ===")
    r3 = c.get(f"{base}/v1/enterprise/settings/integrations/ldap", headers=headers)
    d3 = r3.json().get("data", [])
    print(f"LDAP configs: {len(d3)}")
    for cfg in d3:
        print(f"  {cfg.get('config_name','?')} | {cfg.get('server_url','?')} | enabled={cfg.get('is_enabled')}")

    # 4. DC OS versions
    print("\n=== 4. DC OS versions ===")
    r4 = c.get(f"{base}/v1/enterprise/dc", headers=headers)
    dcs = r4.json().get("data", [])
    for dc in dcs:
        if dc["dc_ip_address"].startswith("192.168"):
            print(f"  {dc['dc_hostname']} | {dc['os_version']}")

    # 5. DFS-R replication
    print("\n=== 5. DFS-R ===")
    r5 = c.get(f"{base}/v1/enterprise/dfs/replication-status", headers=headers)
    d5 = r5.json().get("data", [])
    print(f"DFS-R links: {len(d5)}")
    for link in d5:
        print(f"  {link.get('source_site','?')} -> {link.get('target_site','?')} | {link.get('link_status','?')}")

    # 6. PKI templates
    print("\n=== 6. PKI templates ===")
    r6 = c.get(f"{base}/v1/enterprise/pki/templates", headers=headers)
    d6 = r6.json().get("data", [])
    print(f"PKI templates: {len(d6)}")
    for t in d6:
        print(f"  {t.get('template_name','?')} | {t.get('usage_scenario','?')} | key={t.get('key_length','?')} | days={t.get('validity_period_days','?')}")

    # 7. PKI expiring
    print("\n=== 7. PKI expiring ===")
    r7 = c.get(f"{base}/v1/enterprise/pki/expiring?days=30", headers=headers)
    d7 = r7.json().get("data", [])
    print(f"Expiring certs: {len(d7)}")

    # 8. External integrations
    print("\n=== 8. External integrations ===")
    r8 = c.get(f"{base}/v1/enterprise/settings/integrations/external", headers=headers)
    d8 = r8.json().get("data", [])
    print(f"External integrations: {len(d8)}")
    for ext in d8:
        print(f"  {ext.get('integration_name','?')} | {ext.get('integration_type','?')} | status={ext.get('connection_status','?')}")