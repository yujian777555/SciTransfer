$art = "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts"
$script = "C:\Users\于舰\XiaomiMiMoProjects\SciTransfer\scripts\download_sab_artifacts.py"
Remove-Item "$art\benchmark_verified.zip" -ErrorAction SilentlyContinue
$log = "$art\download.log"
$err = "$art\download.err"
Start-Process -FilePath "python" -ArgumentList "`"$script`"","`"$art`"" -RedirectStandardOutput $log -RedirectStandardError $err
Write-Host "bg download started"
Start-Sleep -Seconds 10
if (Test-Path $log) { Get-Content $log | Select-Object -Last 12 } else { Write-Host "no log" }
if (Test-Path $err) { Get-Content $err | Select-Object -Last 8 }
