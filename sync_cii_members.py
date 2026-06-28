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

def run_rpcclient(command):
    cmd = [
        'rpcclient', '-U', f'{ADMIN_USER}%{ADMIN_PASS}',
        '-W', DOMAIN, '-I', DC_IP,
        '-c', command, 'dcser1'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.stdout

def psql_exec(sql):
    cmd = ['psql', '-h', '127.0.0.1', '-U', 'aduser', '-d', 'adbizsys', '-c', sql]
    env = {'PGPASSWORD': 'Aduser@2026!', 'PATH': '/usr/bin:/bin'}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=10)
    if 'ERROR' in result.stderr:
        print(f"  SQL ERROR: {result.stderr.strip()}")
    return result

def escape_sql(s):
    if s is None:
        return 'NULL'
    return "'" + s.replace("'", "''") + "'"

def get_user_rid_to_dn():
    output = run_rpcclient('enumdomusers')
    rid_map = {}
    for line in output.strip().split('\n'):
        match = re.match(r'user:\[(.+?)\]\s+rid:\[([0-9a-fx]+)\]', line)
        if match:
            name = match.group(1)
            rid = int(match.group(2), 16)
            if name.endswith('$'):
                continue
            if name in ('Administrator', 'Guest', 'krbtgt'):
                if name == 'Administrator':
                    dn = f'CN=Administrator,CN=Users,{BASE_DN}'
                elif name == 'Guest':
                    dn = f'CN=Guest,CN=Users,{BASE_DN}'
                else:
                    dn = f'CN=krbtgt,CN=Users,{BASE_DN}'
            else:
                dn = f'CN={name},OU=scii,{BASE_DN}'
            rid_map[rid] = {'name': name, 'dn': dn}
    return rid_map

def sync_group_members():
    print("=== Syncing Group Members ===")
    user_rid_map = get_user_rid_to_dn()
    print(f"  User RID map: {len(user_rid_map)} users")
    
    total = 0
    for group_name, group_info in CUSTOM_GROUPS.items():
        group_dn = group_info['dn']
        group_rid = group_info['rid']
        print(f"\n  Processing: {group_name} (RID: {hex(group_rid)})")
        
        try:
            output = run_rpcclient(f'querygroupmem {hex(group_rid)}')
            psql_exec(f"DELETE FROM ad_group_members WHERE group_dn = {escape_sql(group_dn)}")
            
            member_rids = []
            for line in output.strip().split('\n'):
                match = re.search(r'rid:\[([0-9a-fx]+)\]', line)
                if match:
                    member_rids.append(int(match.group(1), 16))
            
            for rid in member_rids:
                user_info = user_rid_map.get(rid)
                if user_info:
                    member_dn = user_info['dn']
                    member_name = user_info['name']
                else:
                    member_dn = f"CN=rid_{hex(rid)},{BASE_DN}"
                    member_name = f"rid_{hex(rid)}"
                
                sql = f"""INSERT INTO ad_group_members (group_dn, member_dn, member_type, synced_at, created_at)
                          VALUES ({escape_sql(group_dn)}, {escape_sql(member_dn)}, 'user', NOW(), NOW())"""
                psql_exec(sql)
                total += 1
                print(f"    {member_name} -> {group_name}")
                
        except Exception as ex:
            print(f"    Error: {ex}")
    
    print(f"\n  Total Group Members: {total}")
    return total

if __name__ == '__main__':
    sync_group_members()