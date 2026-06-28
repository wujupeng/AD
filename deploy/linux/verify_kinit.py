import subprocess
result = subprocess.run(
    ['kinit', 'Administrator@COMPANY.LOCAL'],
    input=b'P@ssw0rd2026!\n',
    capture_output=True,
    timeout=15
)
print("stdout:", result.stdout.decode())
print("stderr:", result.stderr.decode())
print("returncode:", result.returncode)

if result.returncode == 0:
    result2 = subprocess.run(['klist'], capture_output=True, timeout=5)
    print("klist:", result2.stdout.decode())