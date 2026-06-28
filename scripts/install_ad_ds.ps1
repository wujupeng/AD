$ErrorActionPreference = 'Stop'
$logFile = 'C:\ad_ds_install_log.txt'

function Write-Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts - $msg" | Out-File -Append -FilePath $logFile -Encoding UTF8
}

Write-Log "=== Starting AD DS Installation ==="

try {
    Write-Log "Checking current AD DS feature status..."
    $feature = Get-WindowsFeature -Name AD-Domain-Services
    Write-Log "AD-Domain-Services Installed: $($feature.Installed)"
    Write-Log "AD-Domain-Services InstallState: $($feature.InstallState)"

    if ($feature.Installed) {
        Write-Log "AD DS is already installed. Skipping installation."
    } else {
        Write-Log "Installing AD-Domain-Services with management tools..."
        $result = Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
        Write-Log "Installation Success: $($result.Success)"
        Write-Log "Restart Needed: $($result.RestartNeeded)"
        Write-Log "Exit Code: $($result.ExitCode)"

        if (-not $result.Success) {
            Write-Log "ERROR: AD DS installation failed!"
            Write-Log "Error message: $($result.ErrorMessage)"
        }
    }

    Write-Log "Verifying installation..."
    $verify = Get-WindowsFeature -Name AD-Domain-Services
    Write-Log "After install - AD-Domain-Services Installed: $($verify.Installed)"

    $rsat = Get-WindowsFeature -Name RSAT-AD-AdminCenter
    Write-Log "RSAT-AD-AdminCenter Installed: $($rsat.Installed)"

    $rsatds = Get-WindowsFeature -Name RSAT-ADDS-Tools
    Write-Log "RSAT-ADDS-Tools Installed: $($rsatds.Installed)"

    Write-Log "=== AD DS Installation Complete ==="
}
catch {
    Write-Log "EXCEPTION: $_"
}