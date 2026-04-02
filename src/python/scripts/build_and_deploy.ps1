<#
.SYNOPSIS
    Build and deploy a pywinui app on Windows.

.DESCRIPTION
    Step-by-step script that:
      1. Installs pywinui (if needed)
      2. Builds the app into dist/
      3. Optionally creates an MSIX package for Windows deployment

.PARAMETER ProjectDir
    Path to the pywinui project directory (contains pywinui.toml).

.PARAMETER SkipMsix
    Skip MSIX packaging (just produce the PyInstaller output).

.EXAMPLE
    .\build_and_deploy.ps1 -ProjectDir .\samples\HelloWorld
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectDir = ".",

    [switch]$SkipMsix
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectDir

Write-Host "`n=== pywinui Build & Deploy ===" -ForegroundColor Cyan

# ── Step 1: Check prerequisites ─────────────────────────────────────────

Write-Host "`n[1/5] Checking prerequisites..." -ForegroundColor Yellow

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python not found. Install Python 3.10+ from https://python.org"
}
Write-Host "  Python: $($python.Source)"

# Check pywinui is installed
$pywinuiCheck = python -c "import pywinui" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing pywinui..." -ForegroundColor Gray
    pip install pywinui
}
Write-Host "  pywinui: OK"

# Check PyInstaller
$piCheck = python -c "import PyInstaller" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing PyInstaller..." -ForegroundColor Gray
    pip install pyinstaller
}
Write-Host "  PyInstaller: OK"

# ── Step 2: Validate project ────────────────────────────────────────────

Write-Host "`n[2/5] Validating project..." -ForegroundColor Yellow

if (-not (Test-Path "pywinui.toml")) {
    Write-Error "pywinui.toml not found in $ProjectDir. Is this a pywinui project?"
}
Write-Host "  pywinui.toml: found"

$config = python -c "import toml; c=toml.load('pywinui.toml'); print(c['project']['name'])" 2>&1
$appName = $config.Trim()
Write-Host "  App name: $appName"

# ── Step 3: Build with PyInstaller ──────────────────────────────────────

Write-Host "`n[3/5] Building '$appName'..." -ForegroundColor Yellow
pywinui build
if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed."
}

$distDir = Join-Path "dist" $appName
Write-Host "  Output: $distDir"

# ── Step 4: Optional MSIX packaging ────────────────────────────────────

if (-not $SkipMsix) {
    Write-Host "`n[4/5] Creating MSIX package..." -ForegroundColor Yellow

    $makeappx = Get-Command makeappx.exe -ErrorAction SilentlyContinue
    if (-not $makeappx) {
        Write-Host "  makeappx.exe not found – skipping MSIX." -ForegroundColor Gray
        Write-Host "  Install Windows SDK to enable MSIX packaging."
        Write-Host "  The PyInstaller output in dist/ is still deployable."
    }
    else {
        $msixDir = Join-Path "dist" "msix"
        New-Item -ItemType Directory -Force -Path $msixDir | Out-Null

        # Create AppxManifest.xml
        $manifest = @"
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities">
  <Identity Name="$appName" Version="1.0.0.0" Publisher="CN=Developer" />
  <Properties>
    <DisplayName>$appName</DisplayName>
    <PublisherDisplayName>pywinui Developer</PublisherDisplayName>
    <Logo>assets\icon.png</Logo>
  </Properties>
  <Resources>
    <Resource Language="en-us" />
  </Resources>
  <Applications>
    <Application Id="App" Executable="$appName.exe" EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="$appName" Description="Built with pywinui"
        Square150x150Logo="assets\icon.png" Square44x44Logo="assets\icon.png"
        BackgroundColor="transparent" />
    </Application>
  </Applications>
  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
  </Capabilities>
</Package>
"@
        $manifest | Out-File -FilePath (Join-Path $distDir "AppxManifest.xml") -Encoding utf8

        $msixPath = Join-Path $msixDir "$appName.msix"
        makeappx.exe pack /d $distDir /p $msixPath /o
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  MSIX: $msixPath"
        }
        else {
            Write-Host "  MSIX packaging failed – PyInstaller output still available."
        }
    }
}
else {
    Write-Host "`n[4/5] Skipping MSIX (--SkipMsix)." -ForegroundColor Gray
}

# ── Step 5: Summary ────────────────────────────────────────────────────

Write-Host "`n[5/5] Done!" -ForegroundColor Green
Write-Host ""
Write-Host "  Distributable:  $distDir"
Write-Host "  Run locally:    $distDir\$appName.exe"
Write-Host ""
Write-Host "  Deploy options:" -ForegroundColor Cyan
Write-Host "    1. Copy dist/$appName/ folder to target machine"
Write-Host "    2. Use MSIX (if built) for Windows Store / sideload"
Write-Host "    3. Zip dist/$appName/ and share directly"
Write-Host ""
