# ============================================================
#  RUN ALL: Server + Localtunnel + Dashboard + 2 Wokwi CLI
# ============================================================
param(
    [string]$LocaltunnelSubdomain = "iot-datn",
    [string]$WokwiToken = ""
)

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ErrorActionPreference = "Continue"

# --- Check Wokwi CLI Token ---
if (-not $WokwiToken) {
    $WokwiToken = $env:WOKWI_CLI_TOKEN
}
if (-not $WokwiToken) {
    Write-Host "=== WOKWI CLI TOKEN ===" -ForegroundColor Yellow
    Write-Host "Ban can API token de chay Wokwi local."
    Write-Host "1. Vao https://wokwi.com/dashboard/ci (dang nhap Wokwi)"
    Write-Host "2. Tao token -> copy"
    Write-Host "3. Set env: `$env:WOKWI_CLI_TOKEN = 'token-cua-ban'"
    Write-Host "   Hoac chay: .\run_all.ps1 -WokwiToken 'token-cua-ban'"
    Write-Host ""
    Write-Host "Khong co token? Chay Python simulator thay the:"
    Write-Host "  python server\simulator.py"
    Write-Host ""
    exit 1
}
$env:WOKWI_CLI_TOKEN = $WokwiToken

$wokwi_cli = Join-Path $PSScriptRoot "wokwi-cli.exe"
if (-not (Test-Path $wokwi_cli)) {
    Write-Host "[!] Thieu wokwi-cli.exe trong thu muc runner" -ForegroundColor Red
    exit 1
}

# --- Kill old processes ---
Get-Process -Name "python", "node", "wokwi-cli" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep 1

# --- Start Server ---
Write-Host "=== 1. Khoi dong Server ===" -ForegroundColor Green
$serverJob = Start-Job -ScriptBlock {
    param($d)
    Set-Location $d
    python server\init_db.py 2>&1 | Out-Null
    python server\app.py
} -ArgumentList $root

Start-Sleep 2

# --- Start Localtunnel ---
Write-Host "=== 2. Khoi dong Localtunnel ===" -ForegroundColor Green
$ltJob = Start-Job -ScriptBlock {
    param($sub)
    lt --port 5000 --subdomain $sub 2>&1 | Out-Null
} -ArgumentList $LocaltunnelSubdomain

Start-Sleep 3

# --- Start Dashboard ---
Write-Host "=== 3. Khoi dong Dashboard ===" -ForegroundColor Green
$dashJob = Start-Job -ScriptBlock {
    param($d)
    Set-Location $d
    python -m streamlit run server\dashboard.py
} -ArgumentList $root

Start-Sleep 5

# --- Start Wokwi Xi_01 ---
Write-Host "=== 4. Khoi dong Wokwi Xi_01 ===" -ForegroundColor Green
$xi01Dir = Join-Path $root "wokwi\xi_01"
$xi01Job = Start-Job -ScriptBlock {
    param($cli, $dir)
    & $cli $dir
} -ArgumentList $wokwi_cli, $xi01Dir

# --- Start Wokwi Xi_02 ---
Write-Host "=== 5. Khoi dong Wokwi Xi_02 ===" -ForegroundColor Green
$xi02Dir = Join-Path $root "wokwi\xi_02"
$xi02Job = Start-Job -ScriptBlock {
    param($cli, $dir)
    & $cli $dir
} -ArgumentList $wokwi_cli, $xi02Dir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DANG CHAY: Server + Dashboard + 2 Wokwi" -ForegroundColor Cyan
Write-Host "  Dashboard: http://localhost:8501" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Nhan Ctrl+C de dung tat ca." -ForegroundColor Yellow

# Wait for any job to finish (blocking)
while ($true) {
    Start-Sleep 1
    $running = @($serverJob, $dashJob, $xi01Job, $xi02Job) | Where-Object { $_.State -eq "Running" }
    if ($running.Count -lt 3) {
        Write-Host "[!] Mot tien trinh da dung. Dang tat..." -ForegroundColor Red
        break
    }
}

# Cleanup
@($serverJob, $ltJob, $dashJob, $xi01Job, $xi02Job) | Where-Object { $_.State -eq "Running" } | Stop-Job
Get-Process -Name "python", "node", "wokwi-cli" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "Da dung toan bo." -ForegroundColor Green
