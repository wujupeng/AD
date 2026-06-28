import subprocess
import sys
import time

DC_IP = '******'
DOMAIN = 'CII'
USER = 'Administrator'
PASS = '*****'

reg_content = """Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\NTDS\\Parameters]
"LDAPServerIntegrity"=dword:00000000

[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\NTDS\\Parameters]
"LDAPEnforceChannelBinding"=dword:00000000
"""

with open('/tmp/ldap_fix.reg', 'w') as f:
    f.write(reg_content)

print("Uploading reg file to DC...")
cmd = [
    'smbclient', '-U', f'{USER}%{PASS}', '-W', DOMAIN,
    f'//{DC_IP}/C$', '-c', 'put /tmp/ldap_fix.reg Windows\\Temp\\ldap_fix.reg'
]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
print(f"Upload result: {r.stdout.strip()}")
if r.returncode != 0:
    print(f"Upload error: {r.stderr.strip()}")
    sys.exit(1)

print("Creating scheduled task to import reg file...")
ps_script = 'reg import C:\\Windows\\Temp\\ldap_fix.reg'
cmd2 = [
    'smbclient', '-U', f'{USER}%{PASS}', '-W', DOMAIN,
    f'//{DC_IP}/C$', '-c', 'put /dev/null Windows\\Temp\\run_fix.flag'
]
subprocess.run(cmd2, capture_output=True, text=True, timeout=10)

print("Attempting winexe to run reg import...")
cmd3 = [
    'winexe', '-U', f'{DOMAIN}/{USER}%{PASS}',
    f'//{DC_IP}',
    f'cmd /c reg import C:\\Windows\\Temp\\ldap_fix.reg'
]
try:
    r3 = subprocess.run(cmd3, capture_output=True, text=True, timeout=20)
    print(f"Winexe result: {r3.stdout.strip()}")
    print(f"Winexe stderr: {r3.stderr.strip()}")
except subprocess.TimeoutExpired:
    print("Winexe timed out")
except Exception as e:
    print(f"Winexe error: {e}")

print("\nVerifying upload...")
cmd4 = [
    'smbclient', '-U', f'{USER}%{PASS}', '-W', DOMAIN,
    f'//{DC_IP}/C$', '-c', 'ls Windows\\Temp\\ldap_fix.reg'
]
r4 = subprocess.run(cmd4, capture_output=True, text=True, timeout=10)
print(f"File check: {r4.stdout.strip()}")