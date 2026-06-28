$ErrorActionPreference = 'Continue'
$logFile = 'C:\fix_dns_log.txt'

function Write-Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts - $msg" | Out-File -Append -FilePath $logFile -Encoding UTF8
}

Write-Log "=== Fixing DNS and Registering DC Records ==="

try {
    Write-Log "Step 1: Checking current DNS settings..."
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1
    $dns = Get-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4
    Write-Log "Current DNS: $($dns.ServerAddresses -join ', ')"

    Write-Log "Step 2: Setting DNS to 127.0.0.1 (self) as primary, 192.168.2.88 as secondary..."
    Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses @('127.0.0.1','192.168.2.88')
    Write-Log "DNS updated."

    Write-Log "Step 3: Registering DNS records..."
    ipconfig /registerdns 2>&1 | ForEach-Object { Write-Log "  registerdns: $_" }

    Write-Log "Step 4: Running nltest to register DC..."
    nltest /dsregdns 2>&1 | ForEach-Object { Write-Log "  dsregdns: $_" }

    Write-Log "Step 5: Forcing replication from primary DC..."
    repadmin /syncall /A /d /e 2>&1 | ForEach-Object { Write-Log "  syncall: $_" }

    Write-Log "Step 6: Checking replication partners..."
    repadmin /showrepl 2>&1 | Select-Object -First 30 | ForEach-Object { Write-Log "  showrepl: $_" }

    Write-Log "Step 7: Running dcdiag /test:DNS..."
    dcdiag /test:DNS 2>&1 | Select-Object -First 40 | ForEach-Object { Write-Log "  dns-test: $_" }

    Write-Log "Step 8: Verifying AD functionality..."
    Import-Module ActiveDirectory
    $dc = Get-ADDomainController
    Write-Log "HostName: $($dc.HostName)"
    Write-Log "Domain: $($dc.Domain)"
    Write-Log "Site: $($dc.Site)"
    Write-Log "IsGlobalCatalog: $($dc.IsGlobalCatalog)"

    $users = Get-ADUser -Filter * -Properties SamAccountName
    Write-Log "Total users: $($users.Count)"

    $groups = Get-ADGroup -Filter *
    Write-Log "Total groups: $($groups.Count)"

    Write-Log "=== DNS Fix Complete ==="
}
catch {
    Write-Log "EXCEPTION: $_"
}