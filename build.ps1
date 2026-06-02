#requires -Version 5.1
<#
.SYNOPSIS
    Build PC Monitor Serial Sender into a standalone Windows EXE.

.DESCRIPTION
    Ensures PyInstaller is installed, cleans previous build output, then builds
    from PC-Monitor-Sender.spec. The result is dist\PC-Monitor-Sender.exe.

.EXAMPLE
    .\build.ps1
        Build using the local Python / virtual environment.

.EXAMPLE
    .\build.ps1 -Clean
        Remove build\ and dist\ first, then build fresh.
#>
[CmdletBinding()]
param(
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

# Prefer a local .venv if one exists, otherwise fall back to PATH python.
$python = if (Test-Path '.\.venv\Scripts\python.exe') {
    '.\.venv\Scripts\python.exe'
} else {
    'python'
}
Write-Host "Using Python: $python" -ForegroundColor Cyan

# Make sure PyInstaller is available. (Probe via pip so a missing module
# doesn't throw under ErrorActionPreference='Stop'; avoid redirecting native
# stderr, which PowerShell 5.1 would wrap into a terminating error.)
& $python -m pip show pyinstaller | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'PyInstaller not found - installing...' -ForegroundColor Yellow
    & $python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) { throw 'Failed to install PyInstaller.' }
}

if ($Clean) {
    Write-Host 'Cleaning build\ and dist\ ...' -ForegroundColor Yellow
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue '.\build', '.\dist'
}

Write-Host 'Building EXE from PC-Monitor-Sender.spec ...' -ForegroundColor Cyan
& $python -m PyInstaller --noconfirm 'PC-Monitor-Sender.spec'
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }

$exe = Join-Path $PSScriptRoot 'dist\PC-Monitor-Sender.exe'
if (Test-Path $exe) {
    Write-Host "`nBuild complete:" -ForegroundColor Green
    Write-Host "  $exe" -ForegroundColor Green
} else {
    throw "Build reported success but $exe was not found."
}
