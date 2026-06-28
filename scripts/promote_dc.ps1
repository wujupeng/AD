$ErrorActionPreference = 'Stop'
$logFile = 'C:\promote_dc_log.txt'

function Write-Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts - $msg" | Out-File -Append -FilePath $logFile -Encoding UTF8
}

Write-Log "=== Starting DC Promotion for cii.sh.cn ==="

try {
    Write-Log "Step 1: Setting DNS to point to existing DC (192.168.2.88)..."
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1
    Write-Log "Network Adapter: $($adapter.Name) (Index: $($adapter.ifIndex))"

    Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses @('192.168.2.88','8.8.8.8')
    Write-Log "DNS set to 192.168.2.88 (primary), 8.8.8.8 (secondary)"

    Start-Sleep -Seconds 3

    Write-Log "Step 2: Testing DNS resolution for cii.sh.cn..."
    try {
        $dnsResult = Resolve-DnsName -Name 'cii.sh.cn' -ErrorAction Stop
        Write-Log "DNS resolution successful: $($dnsResult.IPAddress -join ', ')"
    } catch {
        Write-Log "DNS resolution failed: $_"
        Write-Log "Trying nslookup..."
        $nsResult = nslookup cii.sh.cn 2>&1 | Out-String
        Write-Log "nslookup result: $nsResult"
    }

    Write-Log "Step 3: Testing connectivity to existing DC..."
    $tcp389 = Test-NetConnection -ComputerName 192.168.2.88 -Port 389 -WarningAction SilentlyContinue
    Write-Log "TCP 389 to 192.168.2.88: TcpTestSucceeded=$($tcp389.TcpTestSucceeded)"

    Write-Log "Step 4: Installing AD DS Deployment module..."
    Import-Module ADDSDeployment
    Write-Log "ADDSDeployment module loaded."

    Write-Log "Step 5: Promoting to additional domain controller for cii.sh.cn..."
    Write-Log "This may take several minutes..."

    $safeModePassword = ConvertTo-SecureString -String 'SafeModeP@ss2026!' -AsPlainText -Force

    $result = Install-ADDSDomainController `
        -DomainName 'cii.sh.cn' `
        -SiteName 'Default-First-Site-Name' `
        -SafeModeAdministratorPassword $safeModePassword `
        -Credential (New-Object System.Management.Automation.PSCredential('cii.sh.cn\Administrator', (ConvertTo-SecureString -String 'Htkiss@01' -AsPlainText -Force))) `
        -NoGlobalCatalog:$false `
        -InstallDns:$true `
        -Force:$true `
        -NoRebootOnCompletion:$true

    Write-Log "DC Promotion result: $($result | Out-String)"
    Write-Log "=== DC Promotion Completed - REBOOT REQUIRED ==="
}
catch {
    Write-Log "EXCEPTION: $_"
    Write-Log "=== DC Promotion FAILED ==="
}