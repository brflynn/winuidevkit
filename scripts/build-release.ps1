<#
.SYNOPSIS
    Build release artifacts for WinUIDevKit.

.DESCRIPTION
    Packages each language pack into a zip ready for GitHub release upload.
    Produces:
      - install.ps1                (the installer script itself)
      - winuidevkit-python.zip     (Python wheel + SDK installer)
      - winuidevkit-rust.zip       (project template + CLI wrapper + SDK installer)
      - winuidevkit-go.zip         (project template + CLI wrapper + SDK installer)
      - winuidevkit-nodejs.zip     (project template + CLI wrapper + SDK installer)
      - winuidevkit-swift.zip      (project template + CLI wrapper + SDK installer)

.PARAMETER OutputDir
    Directory to place the artifacts. Defaults to <repo>/release-artifacts/

.PARAMETER Tag
    Version tag for the release (e.g. "v0.1.0").
#>

[CmdletBinding()]
param(
    [string]$OutputDir,
    [string]$Tag = "v0.1.0"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

if (-not $OutputDir) {
    $OutputDir = Join-Path $RepoRoot "release-artifacts"
}

if (Test-Path $OutputDir) {
    Remove-Item $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

Write-Host "Building WinUIDevKit $Tag release artifacts..." -ForegroundColor Cyan
Write-Host "  Repo root:  $RepoRoot"
Write-Host "  Output dir: $OutputDir"
Write-Host ""

# ── Helper: stage common files ───────────────────────────────────────────

function Stage-CommonFiles {
    param([string]$StageDir)

    # SDK installer
    $sdkDir = Join-Path $StageDir "sdk"
    New-Item -ItemType Directory -Path $sdkDir -Force | Out-Null
    Copy-Item (Join-Path $RepoRoot "src\core\sdk\Install-WinAppSdk.ps1") $sdkDir

    # XAML templates
    $tplDir = Join-Path $StageDir "xaml-templates"
    New-Item -ItemType Directory -Path $tplDir -Force | Out-Null
    Copy-Item (Join-Path $RepoRoot "src\core\xaml-templates\*") $tplDir -Recurse

    # Manifests
    $manDir = Join-Path $StageDir "manifests"
    New-Item -ItemType Directory -Path $manDir -Force | Out-Null
    Copy-Item (Join-Path $RepoRoot "src\core\manifests\*") $manDir -Recurse
}

function Stage-CLIWrapper {
    param([string]$StageDir, [string]$Language)

    # Copy the universal PowerShell CLI
    Copy-Item (Join-Path $RepoRoot "scripts\winuidev.ps1") $StageDir

    # Create a .cmd wrapper so 'winuidev' works from cmd/powershell
    $cmdContent = @"
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0winuidev.ps1" %*
"@
    Set-Content (Join-Path $StageDir "winuidev.cmd") -Value $cmdContent -Encoding ASCII
}

# ── 1. Python ────────────────────────────────────────────────────────────

Write-Host "[1/5] Python..." -ForegroundColor Yellow
$pyStage = Join-Path $OutputDir "_stage\python"
New-Item -ItemType Directory -Path $pyStage -Force | Out-Null

# Build the wheel
$pySrc = Join-Path $RepoRoot "src\python"
Push-Location $pySrc
try {
    & python -m pip install build --quiet 2>&1 | Out-Null
    & python -m build --wheel --outdir $pyStage 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Python wheel build failed. Trying sdist..."
        & python -m build --sdist --outdir $pyStage 2>&1 | Out-Null
    }
}
catch {
    Write-Warning "Python build failed: $_"
    # Fallback: do a pip wheel
    & python -m pip wheel $pySrc --wheel-dir $pyStage --no-deps --quiet 2>&1 | Out-Null
}
finally {
    Pop-Location
}

Stage-CommonFiles $pyStage
Compress-Archive -Path "$pyStage\*" -DestinationPath (Join-Path $OutputDir "winuidevkit-python.zip") -Force
Write-Host "  Created winuidevkit-python.zip" -ForegroundColor Green

# ── 2. Rust ──────────────────────────────────────────────────────────────

Write-Host "[2/5] Rust..." -ForegroundColor Yellow
$rustStage = Join-Path $OutputDir "_stage\rust"
New-Item -ItemType Directory -Path $rustStage -Force | Out-Null

# Copy library source (users add as a path dep or we publish as a crate)
Copy-Item (Join-Path $RepoRoot "src\rust\*") $rustStage -Recurse

# Copy example as the init template
$rustTemplate = Join-Path $rustStage "template"
Copy-Item (Join-Path $RepoRoot "examples\rust-helloworld") $rustTemplate -Recurse

Stage-CommonFiles $rustStage
Stage-CLIWrapper $rustStage "rust"
Compress-Archive -Path "$rustStage\*" -DestinationPath (Join-Path $OutputDir "winuidevkit-rust.zip") -Force
Write-Host "  Created winuidevkit-rust.zip" -ForegroundColor Green

# ── 3. Go ────────────────────────────────────────────────────────────────

Write-Host "[3/5] Go..." -ForegroundColor Yellow
$goStage = Join-Path $OutputDir "_stage\go"
New-Item -ItemType Directory -Path $goStage -Force | Out-Null

Copy-Item (Join-Path $RepoRoot "src\go\*") $goStage -Recurse

$goTemplate = Join-Path $goStage "template"
Copy-Item (Join-Path $RepoRoot "examples\go-helloworld") $goTemplate -Recurse

Stage-CommonFiles $goStage
Stage-CLIWrapper $goStage "go"
Compress-Archive -Path "$goStage\*" -DestinationPath (Join-Path $OutputDir "winuidevkit-go.zip") -Force
Write-Host "  Created winuidevkit-go.zip" -ForegroundColor Green

# ── 4. Node.js ───────────────────────────────────────────────────────────

Write-Host "[4/5] Node.js..." -ForegroundColor Yellow
$nodeStage = Join-Path $OutputDir "_stage\nodejs"
New-Item -ItemType Directory -Path $nodeStage -Force | Out-Null

# Copy source (excluding node_modules)
Get-ChildItem (Join-Path $RepoRoot "src\nodejs") -Exclude "node_modules" |
    Copy-Item -Destination $nodeStage -Recurse

$nodeTemplate = Join-Path $nodeStage "template"
Copy-Item (Join-Path $RepoRoot "examples\nodejs-helloworld") $nodeTemplate -Recurse

Stage-CommonFiles $nodeStage
Stage-CLIWrapper $nodeStage "nodejs"
Compress-Archive -Path "$nodeStage\*" -DestinationPath (Join-Path $OutputDir "winuidevkit-nodejs.zip") -Force
Write-Host "  Created winuidevkit-nodejs.zip" -ForegroundColor Green

# ── 5. Swift ─────────────────────────────────────────────────────────────

Write-Host "[5/5] Swift..." -ForegroundColor Yellow
$swiftStage = Join-Path $OutputDir "_stage\swift"
New-Item -ItemType Directory -Path $swiftStage -Force | Out-Null

Copy-Item (Join-Path $RepoRoot "src\swift\*") $swiftStage -Recurse

$swiftTemplate = Join-Path $swiftStage "template"
Copy-Item (Join-Path $RepoRoot "examples\swift-helloworld") $swiftTemplate -Recurse

Stage-CommonFiles $swiftStage
Stage-CLIWrapper $swiftStage "swift"
Compress-Archive -Path "$swiftStage\*" -DestinationPath (Join-Path $OutputDir "winuidevkit-swift.zip") -Force
Write-Host "  Created winuidevkit-swift.zip" -ForegroundColor Green

# ── Copy install.ps1 as a release asset ──────────────────────────────────

Copy-Item (Join-Path $RepoRoot "scripts\install.ps1") $OutputDir
Write-Host ""
Write-Host "  Copied install.ps1" -ForegroundColor Green

# ── Clean up staging ─────────────────────────────────────────────────────

Remove-Item (Join-Path $OutputDir "_stage") -Recurse -Force

# ── Summary ──────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "Release artifacts ready in $OutputDir :" -ForegroundColor Cyan
Get-ChildItem $OutputDir | ForEach-Object {
    $size = if ($_.Length -gt 1MB) { "{0:N1} MB" -f ($_.Length / 1MB) } else { "{0:N0} KB" -f ($_.Length / 1KB) }
    Write-Host "  $($_.Name)  ($size)"
}

Write-Host ""
Write-Host "To publish:" -ForegroundColor Yellow
Write-Host "  gh release create $Tag --title 'WinUIDevKit $Tag' --notes 'Initial release' $OutputDir\*"
