#!/usr/bin/env python3
import subprocess
import sys

def psql_exec(sql):
    cmd = ['psql', '-h', '127.0.0.1', '-U', 'aduser', '-d', 'adbizsys', '-c', sql]
    env = {'PGPASSWORD': 'Aduser@2026!', 'PATH': '/usr/bin:/bin'}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=10)
    print(f"  STDOUT: {result.stdout.strip()}")
    print(f"  STDERR: {result.stderr.strip()}")
    print(f"  RC: {result.returncode}")
    return result

print("=== Test psql connection ===")
psql_exec("SELECT COUNT(*) FROM ad_users;")

print("\n=== Test insert ===")
psql_exec("INSERT INTO ad_ous (dn, ou_name, site_code, synced_at, created_at, updated_at) VALUES ('OU=test,DC=cii,DC=sh,DC=cn', 'test', 'cii_factory', NOW(), NOW(), NOW());")

print("\n=== Check after insert ===")
psql_exec("SELECT ou_name, site_code, dn FROM ad_ous WHERE site_code = 'cii_factory';")

print("\n=== Cleanup test ===")
psql_exec("DELETE FROM ad_ous WHERE dn = 'OU=test,DC=cii,DC=sh,DC=cn';")