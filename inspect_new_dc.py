import subprocess
import sys

DC_IP = '******'
USER = 'administrator'
PASS = '*****'

def winexe_exec(cmd_str):
    cmd = ['winexe', '--ostype=2', '-U', f'{USER}%{PASS}', f'//{DC_IP}', f'cmd /c {cmd_str}']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

print("=== Hostname ===")
print(winexe_exec('hostname'))

print("\n=== OS Info ===")
print(winexe_exec('systeminfo | findstr /B /C:"OS" /C:"System Type" /C:"Domain"'))

print("\n=== Network ===")
print(winexe_exec('ipconfig | findstr /C:"IPv4" /C:"Subnet" /C:"Default Gateway"'))

print("\n=== Domain Status ===")
print(winexe_exec('wmic computersystem get domain,partofdomain /format:list'))

print("\n=== AD DS Role ===")
print(winexe_exec('powershell -Command "Get-WindowsFeature AD-Domain-Services | Format-List Name,InstallState"'))

print("\n=== Services (LDAP/Kerberos/DNS) ===")
print(winexe_exec('powershell -Command "Get-Service -Name NTDS,Kdc,DNS -ErrorAction SilentlyContinue | Format-Table Name,Status -AutoSize"'))