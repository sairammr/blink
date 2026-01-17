# PowerShell script to build Python exe using PyInstaller and copy it to src-tauri/bin
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# PSScriptRoot is application/scripts
$repoRoot = Resolve-Path "$PSScriptRoot\..\.."  # repo root that contains server/ and application/
Push-Location $repoRoot.Path

# Create venv inside server folder
$venvPath = Join-Path $repoRoot 'server\.venv'
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

$python = Join-Path $venvPath 'Scripts\python.exe'
& $python -m pip install --upgrade pip
& $python -m pip install -r server/requirements.txt pyinstaller

# Build the exe (onefile) into server/dist
& $python -m PyInstaller --onefile server/blink.py --distpath server/dist --workpath server/build --specpath server/build

# Copy the executable into application/src-tauri/bin
$distExe = Join-Path $repoRoot 'server\dist\blink.exe'
$destDir = Join-Path $repoRoot 'application\src-tauri\bin'
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
Copy-Item -Force $distExe $destDir

Pop-Location
Write-Host 'Python exe built and copied to src-tauri/bin/blink.exe' -ForegroundColor Green
