Remove-Item "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts\download_fresh.log" -ErrorAction SilentlyContinue
Remove-Item "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts\download_fresh.err" -ErrorAction SilentlyContinue
Start-Process -FilePath "python" -ArgumentList "scripts\download_sab_artifacts.py","C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts" -RedirectStandardOutput "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts\download_fresh.log" -RedirectStandardError "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts\download_fresh.err"
Write-Host "Fresh download started"
Start-Sleep -Seconds 10
Get-Content "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts\download_fresh.log" -ErrorAction SilentlyContinue
Get-Content "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts\download_fresh.err" -ErrorAction SilentlyContinue
