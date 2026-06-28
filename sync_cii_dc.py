import subprocess
import re
import sys

DC_IP = '******'
DOMAIN = 'CII'
ADMIN_USER = 'Administrator'
ADMIN_PASS = '*****'
SITE_CODE = 'cii_factory'
BASE_DN = 'DC=cii,DC=sh,DC=cn'

CUSTOM_GROUPS = {
    'IT': {'rid': 0x450, 'dn': 'CN=IT,OU=scii,DC=cii,DC=sh,DC=cn'},
    'IQC': {'rid': 0x455, 'dn': 'CN=IQC,OU=scii,DC=cii,DC=sh,DC=cn'},
    'HR': {'rid': 0x456, 'dn': 'CN=HR,OU=scii,DC=cii,DC=sh,DC=cn'},
    'Chejian1': {'rid': 0x457, 'dn': 'CN=Chejian1,OU=scii,DC=cii,DC=sh,DC=cn'},
    'CG': {'rid': 0x45b, 'dn': 'CN=CG,OU=scii,DC=cii,DC=sh,DC=cn'},
    'HY': {'rid': 0x45d, 'dn': 'CN=HY,OU=scii,DC=cii,DC=sh,DC=cn'},
    'ERP': {'rid': 0x464, 'dn': 'CN=ERP,OU=scii,DC=cii,DC=sh,DC=cn'},
}

def run_net_ads_search(filter_str, attrs):
    cmd = ['net', 'ads', 'search', '-U', f'{ADMIN_USER}%{ADMIN_PASS}', '-S', DC_IP, filter_str] + attrs
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return parse_net_ads_output(result.stdout)

def parse_net_ads_output(output):
    entries = []
    current = {}
    for line in output.split('\n'):
        line = line.strip()
        if line.startswith('distinguishedName:') or line.startswith('sAMAccountName:') or line.startswith('displayName:') or line.startswith('name:') or line.startswith('description:'):
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if key in current and key != 'description':
                entries.append(current)
                current = {}
            current[key] = value
        elif line == '' and current:
            entries.append(current)
            current = {}
    if current:
        entries.append(current)
    return entries

def run_rpcclient(command):
    cmd = ['rpcclient', '-U', f'{ADMIN_USER}%{ADMIN_PASS}', '-W', DOMAIN, '-I', DC_IP, '-c', command, 'dcser1']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.stdout

def get_user_rid_mapping():
    output = run_rpcclient('enumdomusers')
    rid_map = {}
    for line in output.strip().split('\n'):
        match = re.match(r'user:\[(.+?)\]\s+rid:\[([0-9a-fx]+)\]', line)
        if match:
            name = match.group(1)
            rid = int(match.group(2), 16)
            rid_map[rid] = name
    return rid_map

def psql_exec(sql):
    cmd = ['sudo', '-S', '-u', 'postgres', 'psql', '-d', 'adbizsys', '-c', sql]
    result = subprocess.run(cmd, input='*****\n', capture_output=True, text=True, timeout=10)
    if 'ERROR' in result.stderr or 'ERROR' in result.stdout:
        err = result.stderr.strip() or result.stdout.strip()
        if 'ERROR' in err:
            print(f"  SQL ERROR: {err[:200]}")
    return result

def psql_exists(table, column, value):
    escaped = value.replace("'", "''")
    result = psql_exec(f"SELECT 1 FROM {table} WHERE {column} = '{escaped}' LIMIT 1")
    return '1 row' in result.stdout

def escape_sql(s):
    if s is None:
        return 'NULL'
    return "'" + s.replace("'", "''") + "'"

def sync_ous():
    print("=== Syncing OUs ===")
    entries = run_net_ads_search('(objectClass=organizationalUnit)', ['name', 'distinguishedName', 'description'])
    count = 0
    for entry in entries:
        dn = entry.get('distinguishedName', '')
        name = entry.get('name', '')
        desc = entry.get('description', '')
        if not dn or not name:
            continue
        parent_dn = ','.join(dn.split(',')[1:]) if ',' in dn else None
        if psql_exists('ad_ous', 'dn', dn):
            sql = f"""UPDATE ad_ous SET ou_name = {escape_sql(name)}, description = {escape_sql(desc)}, 
                      site_code = {escape_sql(SITE_CODE)}, synced_at = NOW(), updated_at = NOW() 
                      WHERE dn = {escape_sql(dn)}"""
            psql_exec(sql)
            print(f"  Updated OU: {name}")
        else:
            sql = f"""INSERT INTO ad_ous (dn, ou_name, parent_dn, site_code, description, usn_changed, is_deleted, synced_at, created_at, updated_at)
                      VALUES ({escape_sql(dn)}, {escape_sql(name)}, {escape_sql(parent_dn)}, 
                      {escape_sql(SITE_CODE)}, {escape_sql(desc)}, 0, false, NOW(), NOW(), NOW())"""
            psql_exec(sql)
            print(f"  Added OU: {name}")
        count += 1
    print(f"  Total OUs: {count}")
    return count

def sync_users():
    print("\n=== Syncing Users ===")
    entries = run_net_ads_search('(objectClass=user)', ['sAMAccountName', 'displayName', 'distinguishedName'])
    count = 0
    skipped = 0
    for entry in entries:
        dn = entry.get('distinguishedName', '')
        sam = entry.get('sAMAccountName', '')
        display = entry.get('displayName', '')
        if not dn or not sam:
            continue
        if sam.endswith('$'):
            skipped += 1
            continue
        ou_dn = ','.join(dn.split(',')[1:]) if ',' in dn else None
        sid = f"cii-{sam}-{abs(hash(dn)) % 1000000}"
        if psql_exists('ad_users', 'dn', dn):
            sql = f"""UPDATE ad_users SET username = {escape_sql(sam)}, display_name = {escape_sql(display)},
                      ou_dn = {escape_sql(ou_dn)}, site_code = {escape_sql(SITE_CODE)}, 
                      synced_at = NOW(), updated_at = NOW() WHERE dn = {escape_sql(dn)}"""
            psql_exec(sql)
            print(f"  Updated User: {sam} ({display})")
        else:
            sql = f"""INSERT INTO ad_users (sid, dn, username, display_name, ou_dn, site_code, 
                      user_account_control, is_enabled, is_locked, password_expired, usn_changed, is_deleted, synced_at, created_at, updated_at)
                      VALUES ({escape_sql(sid)}, {escape_sql(dn)}, {escape_sql(sam)}, 
                      {escape_sql(display)}, {escape_sql(ou_dn)}, {escape_sql(SITE_CODE)},
                      512, true, false, false, 0, false, NOW(), NOW(), NOW())"""
            psql_exec(sql)
            print(f"  Added User: {sam} ({display})")
        count += 1
    print(f"  Total Users: {count} (skipped {skipped} computers)")
    return count

def sync_groups():
    print("\n=== Syncing Groups ===")
    entries = run_net_ads_search('(objectClass=group)', ['sAMAccountName', 'distinguishedName', 'description'])
    count = 0
    for entry in entries:
        dn = entry.get('distinguishedName', '')
        sam = entry.get('sAMAccountName', '')
        desc = entry.get('description', '')
        if not dn or not sam:
            continue
        ou_dn = ','.join(dn.split(',')[1:]) if ',' in dn else None
        scope = 'DomainLocal' if 'CN=Builtin' in dn else 'Global'
        if psql_exists('ad_groups', 'dn', dn):
            sql = f"""UPDATE ad_groups SET group_name = {escape_sql(sam)}, description = {escape_sql(desc)},
                      ou_dn = {escape_sql(ou_dn)}, scope = {escape_sql(scope)}, 
                      synced_at = NOW(), updated_at = NOW() WHERE dn = {escape_sql(dn)}"""
            psql_exec(sql)
            print(f"  Updated Group: {sam}")
        else:
            sql = f"""INSERT INTO ad_groups (dn, group_name, description, ou_dn, scope, category, 
                      group_type, usn_changed, is_deleted, synced_at, created_at, updated_at)
                      VALUES ({escape_sql(dn)}, {escape_sql(sam)}, {escape_sql(desc)},
                      {escape_sql(ou_dn)}, {escape_sql(scope)}, 'Security',
                      2, 0, false, NOW(), NOW(), NOW())"""
            psql_exec(sql)
            print(f"  Added Group: {sam}")
        count += 1
    print(f"  Total Groups: {count}")
    return count

def sync_group_members():
    print("\n=== Syncing Group Members ===")
    user_rid_map = get_user_rid_mapping()
    rid_to_dn = {}
    entries = run_net_ads_search('(objectClass=user)', ['sAMAccountName', 'distinguishedName'])
    for e in entries:
        sam = e.get('sAMAccountName', '')
        dn = e.get('distinguishedName', '')
        if sam and dn:
            for rid, name in user_rid_map.items():
                if name == sam:
                    rid_to_dn[rid] = dn
    count = 0
    for group_name, group_info in CUSTOM_GROUPS.items():
        group_dn = group_info['dn']
        group_rid = group_info['rid']
        print(f"  Processing: {group_name}")
        try:
            output = run_rpcclient(f'querygroupmem {hex(group_rid)}')
            psql_exec(f"DELETE FROM ad_group_members WHERE group_dn = {escape_sql(group_dn)}")
            for line in output.strip().split('\n'):
                match = re.search(r'rid:\[([0-9a-fx]+)\]', line)
                if match:
                    rid = int(match.group(1), 16)
                    member_dn = rid_to_dn.get(rid, f"CN=rid_{hex(rid)},{BASE_DN}")
                    sql = f"""INSERT INTO ad_group_members (group_dn, member_dn, member_type, synced_at, created_at)
                              VALUES ({escape_sql(group_dn)}, {escape_sql(member_dn)}, 'user', NOW(), NOW())"""
                    psql_exec(sql)
                    count += 1
                    member_name = user_rid_map.get(rid, f"rid_{hex(rid)}")
                    print(f"    {member_name} -> {group_name}")
        except Exception as ex:
            print(f"    Error: {ex}")
    print(f"  Total Group Members: {count}")
    return count

if __name__ == '__main__':
    try:
        ou_count = sync_ous()
        user_count = sync_users()
        group_count = sync_groups()
        member_count = sync_group_members()
        print(f"\n=== Sync Complete ===")
        print(f"  OUs: {ou_count}")
        print(f"  Users: {user_count}")
        print(f"  Groups: {group_count}")
        print(f"  Group Members: {member_count}")
    except Exception as ex:
        print(f"Sync failed: {ex}")
        raise
