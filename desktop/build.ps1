# Builds the PROWEB HR Windows program:
#   dist\ProwebHR\ProwebHR.exe          portable folder (runs without installing)
#   dist\ProwebHR-Setup-<version>.exe   installer (needs Inno Setup 6: https://jrsoftware.org/isinfo.php)
#
# Usage (from the repo root):  powershell -ExecutionPolicy Bypass -File desktop\build.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = Join-Path $Root "venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Creating virtualenv..."
    python -m venv venv
}

Write-Host "Installing dependencies..."
& $Python -m pip install -q -r requirements-desktop.txt
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

Write-Host "Running tests..."
& $Python -m pytest tests -q -p no:warnings
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
Push-Location jobhunter_crm
& $Python manage.py test tests -v 0
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Django tests failed" }

Write-Host "Collecting static files..."
& $Python manage.py collectstatic --noinput --clear -v 0
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "collectstatic failed" }
Pop-Location

& $Python desktop\make_icon.py

Write-Host "Building exe (PyInstaller)..."
& (Join-Path $Root "venv\Scripts\pyinstaller.exe") desktop\prowebhr.spec --noconfirm --distpath dist --workpath build\pyinstaller --log-level WARN
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
Write-Host "Portable build: $Root\dist\ProwebHR\ProwebHR.exe"

$Iscc = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($Iscc) {
    Write-Host "Building installer (Inno Setup)..."
    & $Iscc /Q desktop\installer.iss
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed" }
    Get-ChildItem dist\ProwebHR-Setup-*.exe | ForEach-Object { Write-Host "Installer: $($_.FullName)" }
} else {
    Write-Host "Inno Setup 6 not found - installer skipped (winget install JRSoftware.InnoSetup)."
}
