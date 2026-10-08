# Non-destructive download starter (R1 fix).
# Does NOT delete existing partial zip; the Python script resumes safely.
$art = "C:\Users\于舰\XiaomiMiMoProjects\sab-artifacts"
$script = "C:\Users\于舰\XiaomiMiMoProjects\SciTransfer\scripts\download_sab_artifacts.py"
$log = "$art\download.log"
$err = "$art\download.err"

# Check existing partial download (do NOT delete)
if (Test-Path "$art\benchmark_verified.zip") {
    $size = (Get-Item "$art\benchmark_verified.zip").Length
    Write-Host "Found existing partial zip: $size bytes — will resume"
} else {
    Write-Host "No existing zip — starting fresh download"
}

Start-Process -FilePath "python" -ArgumentList "`"$script`"","`"$art`"" -RedirectStandardOutput $log -RedirectStandardError $err
Write-Host "Download started (non-destructive resume)"
Start-Sleep -Seconds 10
if (Test-Path $log) { Get-Content $log | Select-Object -Last 12 } else { Write-Host "no log yet" }
if (Test-Path $err) { Get-Content $err | Select-Object -Last 5 }
