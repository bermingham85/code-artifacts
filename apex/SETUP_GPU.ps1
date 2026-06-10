# APEX Network Setup - GPU Machine (DESKTOP-A2MF76F)
# Run as Administrator: Right-click PowerShell > Run as Admin
# One-time setup - links all machines together

Write-Host "=== APEX GPU Machine Setup ===" -ForegroundColor Cyan

# 0. Wake GPU machine via WOL magic packet (CC:28:AA:A9:20:1D = MSFT 5 0)
Write-Host "`n[0/4] Sending WOL magic packet to GPU..." -ForegroundColor Yellow
try {
    $mac = "CC28AAA9201D"
    $target = [System.Net.IPAddress]::Broadcast
    $bytes = [byte[]](,0xFF * 6)
    for ($i = 0; $i -lt 6; $i++) { $bytes += [Convert]::ToByte($mac.Substring($i*2,2),16) }
    for ($i = 0; $i -lt 16; $i++) {
        for ($j = 0; $j -lt 6; $j++) { $bytes += [Convert]::ToByte($mac.Substring($j*2,2),16) }
    }
    $udp = New-Object System.Net.Sockets.UdpClient
    $udp.EnableBroadcast = $true
    $udp.Connect($target, 9)
    $udp.Send($bytes, $bytes.Length) | Out-Null
    $udp.Close()
    Write-Host "  Magic packet sent to CC:28:AA:A9:20:1D" -ForegroundColor Green
    Write-Host "  Waiting 30s for GPU to boot..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
} catch {
    Write-Host "  WOL send failed: $_" -ForegroundColor Red
    Write-Host "  Continuing setup anyway..." -ForegroundColor Yellow
}


Write-Host "`n[1/4] Enabling PowerShell Remoting..." -ForegroundColor Yellow
Enable-PSRemoting -Force -SkipNetworkProfileCheck
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force

# 2. Share key folders
Write-Host "`n[2/4] Creating network shares..." -ForegroundColor Yellow
net share ComfyUI="C:\ComfyUI" /grant:everyone,FULL 2>$null
net share apex="C:\apex" /grant:everyone,FULL 2>$null

# 3. Enable WinRM firewall rules
Write-Host "`n[3/4] Opening firewall for remote management..." -ForegroundColor Yellow
Enable-NetFirewallRule -DisplayName "Windows Remote Management (HTTP-In)"

# 4. Add Tailscale to PATH if not there
Write-Host "`n[4/4] Checking Tailscale..." -ForegroundColor Yellow
$tsPath = "C:\Program Files\Tailscale"
if (Test-Path "$tsPath\tailscale.exe") {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*Tailscale*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$tsPath", "Machine")
        Write-Host "  Added Tailscale to system PATH" -ForegroundColor Green
    }
    & "$tsPath\tailscale.exe" status
} else {
    Write-Host "  Tailscale not found - install from https://tailscale.com/download" -ForegroundColor Red
}

Write-Host "`n=== GPU Setup Complete ===" -ForegroundColor Green
Write-Host "Tailscale name: desktop-a2mf76f"
Write-Host "Tailscale IP:   100.94.158.106"
