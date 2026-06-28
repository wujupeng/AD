import json, subprocess

def psql_exec(sql):
    cmd = ['sudo', '-S', '-u', 'postgres', 'psql', '-d', 'adbizsys', '-c', sql]
    r = subprocess.run(cmd, input='*****\n', capture_output=True, text=True, timeout=10)
    return r.stdout

print("=== Register new server ****** ===")

print("1. Adding to dc_registries...")
psql_exec("""
INSERT INTO dc_registries (dc_hostname, dc_site, dc_ip_address, is_gc, is_dns_integrated, fsmo_roles, health_status, os_version)
VALUES ('WIN-SRV01', 'cluster_test', '******', false, false, '{}', 'healthy', 'Windows Server 2022')
ON CONFLICT (dc_hostname) DO UPDATE SET dc_ip_address = '******', health_status = 'healthy';
""")

print("2. Adding site_config for cluster_test...")
psql_exec("""
INSERT INTO site_configs (site_code, site_name, region, country, subnet_ranges, dc_priority_list, timezone, language, is_active, description, site_display_name)
VALUES ('cluster_test', 'Cluster Test', 'test', 'CN', '192.168.1.0/24', '["WIN-SRV01"]', 'Asia/Shanghai', 'zh-CN', true, '群集测试站点', '群集测试')
ON CONFLICT (site_code) DO UPDATE SET site_display_name = '群集测试';
""")

print("3. Verifying...")
r1 = psql_exec("SELECT dc_hostname, dc_site, dc_ip_address, health_status FROM dc_registries WHERE dc_site = 'cluster_test';")
print(f"DC Registry:\n{r1}")

r2 = psql_exec("SELECT site_code, site_display_name FROM site_configs WHERE site_code = 'cluster_test';")
print(f"Site Config:\n{r2}")

print("\nDone!")