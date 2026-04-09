<#
.SYNOPSIS
    Install WinUIDevKit for your preferred language.

.DESCRIPTION
    Downloads the latest WinUIDevKit release from GitHub and installs the
    language pack of your choice. No repo clone, no package manager required.

.PARAMETER Language
    The language pack to install: python, rust, go, nodejs, swift

.PARAMETER Version
    Specific release tag (e.g. "v0.2.0"). Defaults to "latest".

.PARAMETER InstallDir
    Where to install. Defaults to $env:LOCALAPPDATA\WinUIDevKit

.EXAMPLE
    # Interactive — prompts for language
    irm https://github.com/brflynn/WinUIDevKit/releases/latest/download/install.ps1 | iex

    # Non-interactive
    .\install.ps1 -Language python
#>

[CmdletBinding()]
param(
    [ValidateSet("python", "rust", "go", "nodejs", "swift")]
    [string]$Language,

    [string]$Version = "latest",

    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "WinUIDevKit")
)

$ErrorActionPreference = "Stop"
$RepoOwner = "brflynn"
$RepoName = "WinUIDevKit"

# ── Resolve version ──────────────────────────────────────────────────────
function Get-LatestTag {
    $url = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
    try {
        $release = Invoke-RestMethod -Uri $url -Headers @{ Accept = "application/vnd.github.v3+json" }
        return $release.tag_name
    }
    catch {
        Write-Error "Failed to fetch latest release. Check your network or specify -Version explicitly."
        exit 1
    }
}

if ($Version -eq "latest") {
    Write-Host "Checking latest WinUIDevKit release..." -ForegroundColor Cyan
    $Version = Get-LatestTag
}
Write-Host "Version: $Version" -ForegroundColor Green

# ── Prompt for language if not specified ──────────────────────────────────
if (-not $Language) {
    Write-Host ""
    Write-Host "Which language pack would you like to install?" -ForegroundColor Yellow
    Write-Host "  [1] Python"
    Write-Host "  [2] Rust"
    Write-Host "  [3] Go"
    Write-Host "  [4] Node.js"
    Write-Host "  [5] Swift"
    Write-Host ""
    $choice = Read-Host "Enter number (1-5)"
    $Language = switch ($choice) {
        "1" { "python" }
        "2" { "rust" }
        "3" { "go" }
        "4" { "nodejs" }
        "5" { "swift" }
        default { Write-Error "Invalid choice: $choice"; exit 1 }
    }
}

Write-Host "Installing WinUIDevKit for $Language..." -ForegroundColor Cyan

# ── Download ─────────────────────────────────────────────────────────────
$assetName = "winuidevkit-$Language.zip"
$downloadUrl = "https://github.com/$RepoOwner/$RepoName/releases/download/$Version/$assetName"
$tempZip = Join-Path $env:TEMP $assetName

Write-Host "Downloading $downloadUrl"
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip -UseBasicParsing
}
catch {
    Write-Error "Download failed. Verify the release exists at: $downloadUrl"
    exit 1
}

# ── Extract ──────────────────────────────────────────────────────────────
$langDir = Join-Path $InstallDir $Language
if (Test-Path $langDir) {
    Write-Host "Removing previous installation at $langDir"
    Remove-Item $langDir -Recurse -Force
}
New-Item -ItemType Directory -Path $langDir -Force | Out-Null

Write-Host "Extracting to $langDir"
Expand-Archive -Path $tempZip -DestinationPath $langDir -Force
Remove-Item $tempZip -Force

# ── Language-specific setup ──────────────────────────────────────────────
$binDir = Join-Path $InstallDir "bin"
New-Item -ItemType Directory -Path $binDir -Force | Out-Null

# Store install location so the CLI can find templates + SDK scripts
[Environment]::SetEnvironmentVariable("WINUIDEVKIT_HOME", $langDir, "User")
$env:WINUIDEVKIT_HOME = $langDir

# Persist the chosen language so 'winuidev init' doesn't need -Language
[Environment]::SetEnvironmentVariable("WINUIDEVKIT_LANGUAGE", $Language, "User")
$env:WINUIDEVKIT_LANGUAGE = $Language
Set-Content (Join-Path $InstallDir ".language") -Value $Language -NoNewline

switch ($Language) {
    "python" {
        # Install the wheel into the user's Python environment
        $wheel = Get-ChildItem $langDir -Filter "*.whl" -Recurse | Select-Object -First 1
        if (-not $wheel) {
            Write-Error "No .whl file found in the release archive."
            exit 1
        }
        Write-Host "Installing Python wheel: $($wheel.Name)"
        & python -m pip install $wheel.FullName --force-reinstall --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Error "pip install failed. Ensure Python 3.10+ is installed and on PATH."
            exit 1
        }
        Write-Host "Python pack installed. CLI available as 'winuidev' and 'pywinui'."
    }

    default {
        # All non-Python languages use the PowerShell CLI wrapper
        $cliScript = Get-ChildItem $langDir -Filter "winuidev.ps1" -Recurse | Select-Object -First 1
        if ($cliScript) {
            Copy-Item $cliScript.FullName (Join-Path $binDir "winuidev.ps1") -Force

            # Create a .cmd wrapper so 'winuidev' works from cmd/powershell
            $cmdContent = "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File `"%~dp0winuidev.ps1`" %*"
            Set-Content (Join-Path $binDir "winuidev.cmd") -Value $cmdContent -Encoding ASCII

            Write-Host "$Language CLI installed to $binDir\winuidev.cmd"
        }
        else {
            # Legacy: try prebuilt binary
            $exe = Get-ChildItem $langDir -Filter "winuidev.exe" -Recurse | Select-Object -First 1
            if ($exe) {
                Copy-Item $exe.FullName (Join-Path $binDir "winuidev.exe") -Force
                Write-Host "$Language CLI binary installed to $binDir\winuidev.exe"
            }
            else {
                Write-Warning "No CLI found in the language pack. You may need to update WinUIDevKit."
            }
        }
    }
}

# ── Add bin to PATH (current session + user PATH) ───────────────────────
if ($Language -ne "python") {
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable("PATH", "$binDir;$userPath", "User")
        $env:PATH = "$binDir;$env:PATH"
        Write-Host "Added $binDir to user PATH."
    }
}

# ── Done ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "WinUIDevKit ($Language) installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  winuidev setup          # one-time: install Windows App SDK"
Write-Host "  winuidev init MyApp     # scaffold a new project"
Write-Host "  cd MyApp"
Write-Host "  winuidev run            # launch the app"
Write-Host ""
