<#
.SYNOPSIS
    WinUIDevKit universal CLI — works for all 5 supported languages.

.DESCRIPTION
    Provides a uniform developer workflow for building WinUI3 apps:
      winuidev setup       — install Windows App SDK + language prerequisites
      winuidev init <name> — scaffold a new project
      winuidev run         — launch the app in dev mode
      winuidev build       — package for distribution
      winuidev doctor      — check that all dependencies are installed

.PARAMETER Command
    The CLI command: setup, init, run, build, doctor

.PARAMETER Name
    Project name (required for 'init')

.PARAMETER Language
    Target language: python, rust, go, nodejs, swift
    Auto-detected from project files when omitted.

.EXAMPLE
    winuidev setup
    winuidev init MyApp -Language python
    cd MyApp
    winuidev run
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("setup", "init", "run", "build", "doctor")]
    [string]$Command,

    [Parameter(Position = 1)]
    [string]$Name,

    [ValidateSet("python", "rust", "go", "nodejs", "swift")]
    [string]$Language
)

$ErrorActionPreference = "Stop"

# ── Refresh PATH from registry ───────────────────────────────────────────
# The .cmd wrapper launches with -NoProfile, so recently-installed tools
# (e.g. cargo via rustup, go, node) may not be on the session PATH yet.
$machinePath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
$userPath    = [Environment]::GetEnvironmentVariable("PATH", "User")
$env:PATH    = "$userPath;$machinePath"

# ── Resolve install location ─────────────────────────────────────────────

function Get-InstallHome {
    # WINUIDEVKIT_HOME is set by install.ps1 to the extracted language pack dir
    if ($env:WINUIDEVKIT_HOME -and (Test-Path $env:WINUIDEVKIT_HOME)) {
        return $env:WINUIDEVKIT_HOME
    }
    # Fallback: walk up from this script's location
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    # If script is in an install bin dir, the language pack is a sibling
    $installBase = Split-Path -Parent $scriptDir
    foreach ($lang in @("python","rust","go","nodejs","swift")) {
        $langDir = Join-Path $installBase $lang
        if (Test-Path $langDir) {
            return $langDir
        }
    }
    # Last fallback: repo source layout
    if ($env:WINUIDEVKIT_ROOT -and (Test-Path $env:WINUIDEVKIT_ROOT)) {
        return $env:WINUIDEVKIT_ROOT
    }
    $parent = Split-Path -Parent $scriptDir
    if (Test-Path (Join-Path $parent "src\core")) {
        return $parent
    }
    Write-Error "Cannot find WinUIDevKit installation. Set `$env:WINUIDEVKIT_HOME or reinstall."
    exit 1
}

$PackHome = Get-InstallHome

# ── Language detection ───────────────────────────────────────────────────

function Detect-Language {
    if ($Language) { return $Language }

    # Detect from project files in current directory
    if (Test-Path "pywinui.toml")    { return "python" }
    if (Test-Path "pyproject.toml") {
        $content = Get-Content "pyproject.toml" -Raw
        if ($content -match "pywinui|winuidevkit") { return "python" }
    }
    if (Test-Path "Cargo.toml")      { return "rust" }
    if (Test-Path "go.mod")          { return "go" }
    if (Test-Path "package.json") {
        $pkg = Get-Content "package.json" -Raw | ConvertFrom-Json
        if ($pkg.dependencies.PSObject.Properties.Name -contains "winuidevkit" -or
            $pkg.name -match "winui") {
            return "nodejs"
        }
    }
    if (Test-Path "Package.swift")   { return "swift" }

    return $null
}

# ── SETUP command ────────────────────────────────────────────────────────

function Invoke-Setup {
    $lang = Detect-Language
    Write-Host "WinUIDevKit Setup" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    Write-Host ""

    # Step 1: Install Windows App SDK runtime
    Write-Host "[1/2] Windows App SDK runtime..." -ForegroundColor Yellow
    # Look for SDK installer in the installed pack
    $sdkScript = Join-Path $PackHome "sdk\Install-WinAppSdk.ps1"
    if (-not (Test-Path $sdkScript)) {
        # Repo source layout fallback
        $sdkScript = Join-Path $PackHome "src\core\sdk\Install-WinAppSdk.ps1"
    }
    if (Test-Path $sdkScript) {
        & $sdkScript -Verbose
    }
    else {
        # Fallback: try winget
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "  Installing via winget..."
            winget install --id Microsoft.WindowsAppSDK.1.8 --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
            Write-Host "  Done."
        }
        else {
            Write-Warning "  Could not find Install-WinAppSdk.ps1 or winget. Install WinAppSDK manually."
        }
    }

    # Step 2: Language-specific prerequisites
    Write-Host ""
    Write-Host "[2/2] Language prerequisites..." -ForegroundColor Yellow

    if (-not $lang) {
        Write-Host "  No language specified or detected. Checking all toolchains..." -ForegroundColor Gray
        _Check-AllToolchains
    }
    else {
        _Check-LanguagePrereqs $lang
    }

    Write-Host ""
    Write-Host "Setup complete!" -ForegroundColor Green
    Write-Host "  winuidev init MyApp     # scaffold a new project"
    Write-Host "  cd MyApp"
    Write-Host "  winuidev run"
}

function _Check-AllToolchains {
    $toolchains = @{
        python = "python --version"
        rust   = "rustc --version"
        go     = "go version"
        nodejs = "node --version"
        swift  = "swift --version"
    }
    foreach ($lang in $toolchains.Keys) {
        $cmd = $toolchains[$lang]
        try {
            $result = Invoke-Expression $cmd 2>&1
            Write-Host "  $lang : $result" -ForegroundColor Green
        }
        catch {
            Write-Host "  $lang : not found" -ForegroundColor Red
        }
    }
}

function _Check-LanguagePrereqs {
    param([string]$Lang)

    switch ($Lang) {
        "python" {
            if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
                Write-Error "Python not found. Install Python 3.10+ and add to PATH."
            }
            $ver = python --version 2>&1
            Write-Host "  Python: $ver"

            # Check if pywinui CLI is available
            if (-not (Get-Command pywinui -ErrorAction SilentlyContinue)) {
                Write-Host "  pywinui CLI not found. It should have been installed by install.ps1."
                Write-Host "  Try: pip install pywinui" -ForegroundColor Yellow
            }
            else {
                Write-Host "  pywinui CLI: available" -ForegroundColor Green
            }
        }
        "rust" {
            if (-not (Get-Command rustc -ErrorAction SilentlyContinue)) {
                Write-Error "Rust not found. Install from https://rustup.rs"
            }
            $ver = rustc --version 2>&1
            Write-Host "  Rust: $ver"
        }
        "go" {
            if (-not (Get-Command go -ErrorAction SilentlyContinue)) {
                Write-Error "Go not found. Install from https://go.dev/dl/"
            }
            $ver = go version 2>&1
            Write-Host "  Go: $ver"
        }
        "nodejs" {
            if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
                Write-Error "Node.js not found. Install from https://nodejs.org"
            }
            $ver = node --version 2>&1
            Write-Host "  Node.js: $ver"
        }
        "swift" {
            if (-not (Get-Command swift -ErrorAction SilentlyContinue)) {
                Write-Error "Swift not found. Install Swift for Windows from https://swift.org/download/"
            }
            $ver = swift --version 2>&1 | Select-Object -First 1
            Write-Host "  Swift: $ver"
        }
    }
}

# ── Installed-language lookup ─────────────────────────────────────────────

function _Get-InstalledLanguage {
    # 1. Environment variable set by install.ps1
    $lang = [Environment]::GetEnvironmentVariable("WINUIDEVKIT_LANGUAGE", "User")
    if ($lang -and $lang -in @("python","rust","go","nodejs","swift")) {
        return $lang
    }
    # 2. .language file in the install directory
    $installBase = Split-Path -Parent $PackHome
    $langFile = Join-Path $installBase ".language"
    if (Test-Path $langFile) {
        $lang = (Get-Content $langFile -Raw).Trim()
        if ($lang -in @("python","rust","go","nodejs","swift")) {
            return $lang
        }
    }
    # 3. Infer from WINUIDEVKIT_HOME path (last segment is the language)
    if ($env:WINUIDEVKIT_HOME) {
        $lang = Split-Path -Leaf $env:WINUIDEVKIT_HOME
        if ($lang -in @("python","rust","go","nodejs","swift")) {
            return $lang
        }
    }
    return $null
}

# ── INIT command ─────────────────────────────────────────────────────────

function Invoke-Init {
    if (-not $Name) {
        Write-Error "Usage: winuidev init <project-name> [-Language <lang>]"
        exit 1
    }
    if (-not $Language) {
        # Try to infer from install-time config
        $Language = _Get-InstalledLanguage
    }
    if (-not $Language) {
        Write-Error "Please specify a language: winuidev init $Name -Language <python|rust|go|nodejs|swift>"
        exit 1
    }

    $dest = Join-Path (Get-Location) $Name
    if (Test-Path $dest) {
        Write-Host "Directory '$Name' already exists — skipping scaffold." -ForegroundColor Yellow
        Write-Host "Default language set to '$Language'." -ForegroundColor Green
        # Persist the language choice so future commands use it
        [Environment]::SetEnvironmentVariable("WINUIDEVKIT_LANGUAGE", $Language, "User")
        $env:WINUIDEVKIT_LANGUAGE = $Language
        $installBase = Split-Path -Parent $PackHome
        $langFile = Join-Path $installBase ".language"
        if (Test-Path (Split-Path $langFile)) {
            Set-Content $langFile -Value $Language -NoNewline
        }
        return
    }

    Write-Host "Creating $Language project '$Name'..." -ForegroundColor Cyan

    # Find the template directory in the installed language pack
    $templateDir = Join-Path $PackHome "template"
    if (-not (Test-Path $templateDir)) {
        # Repo source layout fallback: examples/<lang>-helloworld
        $templateDir = Join-Path $PackHome "examples\$Language-helloworld"
    }
    if (-not (Test-Path $templateDir)) {
        Write-Error "Template not found for '$Language'. Reinstall with: .\install.ps1 -Language $Language"
        exit 1
    }

    Copy-Item -Path $templateDir -Destination $dest -Recurse

    # Replace placeholders in all text files
    Get-ChildItem $dest -Recurse -File |
        Where-Object { $_.Extension -in ".py", ".toml", ".xaml", ".rs", ".go", ".ts", ".js", ".json", ".swift", ".md" } |
        ForEach-Object {
            $content = Get-Content $_.FullName -Raw
            $content = $content.Replace("{{PROJECT_NAME}}", $Name)
            $content = $content.Replace("{{APP_NAME}}", $Name)
            Set-Content $_.FullName -Value $content -NoNewline
        }

    Write-Host ""
    Write-Host "Project '$Name' created!" -ForegroundColor Green
    Write-Host "  cd $Name"
    Write-Host "  winuidev run"
}

# ── RUN command ──────────────────────────────────────────────────────────

function Invoke-Run {
    $lang = Detect-Language
    if (-not $lang) {
        Write-Error "Cannot detect project language. Are you in a WinUIDevKit project directory?"
        exit 1
    }

    Write-Host "Running $lang app..." -ForegroundColor Cyan

    switch ($lang) {
        "python" {
            # Use the pywinui CLI if installed, otherwise invoke directly
            if (Get-Command pywinui -ErrorAction SilentlyContinue) {
                & pywinui run
            }
            else {
                $cfg = _Load-PywinuiConfig
                $xaml = $cfg.app.xaml
                $codebehind = $cfg.app.codebehind
                & python -m pywinui_runtime --xaml $xaml --codebehind $codebehind
            }
        }
        "rust" {
            & cargo run
        }
        "go" {
            & go run .
        }
        "nodejs" {
            if (Test-Path "node_modules") {
                & npx ts-node app/main.ts
            }
            else {
                Write-Host "  Installing dependencies..." -ForegroundColor Yellow
                & npm install
                & npx ts-node app/main.ts
            }
        }
        "swift" {
            & swift run
        }
    }
}

# ── BUILD command ────────────────────────────────────────────────────────

function Invoke-Build {
    $lang = Detect-Language
    if (-not $lang) {
        Write-Error "Cannot detect project language. Are you in a WinUIDevKit project directory?"
        exit 1
    }

    Write-Host "Building $lang app..." -ForegroundColor Cyan

    switch ($lang) {
        "python" {
            if (Get-Command pywinui -ErrorAction SilentlyContinue) {
                & pywinui build
            }
            else {
                Write-Host "Install pywinui first: pip install -e $RepoRoot\src\python"
                exit 1
            }
        }
        "rust" {
            & cargo build --release
            Write-Host "Binary at target/release/" -ForegroundColor Green
        }
        "go" {
            & go build -o "$((Get-Item .).Name).exe" .
            Write-Host "Binary built." -ForegroundColor Green
        }
        "nodejs" {
            & npx tsc
            Write-Host "Compiled to dist/" -ForegroundColor Green
        }
        "swift" {
            & swift build -c release
            Write-Host "Binary at .build/release/" -ForegroundColor Green
        }
    }
}

# ── DOCTOR command ───────────────────────────────────────────────────────

function Invoke-Doctor {
    $lang = Detect-Language

    Write-Host "WinUIDevKit Doctor" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    $ok = $true

    # OS check
    Write-Host "  Platform:       $([System.Environment]::OSVersion.VersionString)"
    Write-Host "  Architecture:   $env:PROCESSOR_ARCHITECTURE"

    # Windows App SDK
    $sdkInstalled = $false
    try {
        $pkgs = Get-AppxPackage -Name "Microsoft.WindowsAppRuntime*" 2>$null
        $match = $pkgs | Where-Object { $_.Version -like "1.8.*" }
        if ($match) {
            Write-Host "  WinAppSDK:      installed ($($match.Version))" -ForegroundColor Green
            $sdkInstalled = $true
        }
    }
    catch {}

    if (-not $sdkInstalled) {
        # Check NuGet cache
        $cacheDir = Join-Path $env:LOCALAPPDATA "WinUIDevKit\sdk"
        if (Test-Path $cacheDir) {
            Write-Host "  WinAppSDK:      cached (NuGet)" -ForegroundColor Yellow
        }
        else {
            Write-Host "  WinAppSDK:      NOT FOUND — run: winuidev setup" -ForegroundColor Red
            $ok = $false
        }
    }

    # Language toolchain
    if ($lang) {
        Write-Host "  Project lang:   $lang" -ForegroundColor Green
        _Check-LanguagePrereqs $lang
    }
    else {
        Write-Host "  Project lang:   (not in a project directory)" -ForegroundColor Gray
        _Check-AllToolchains
    }

    Write-Host "=================="
    if ($ok) {
        Write-Host "All checks passed!" -ForegroundColor Green
    }
    else {
        Write-Host "Some checks failed. Run: winuidev setup" -ForegroundColor Red
    }
}

# ── Python config helper ─────────────────────────────────────────────────

function _Load-PywinuiConfig {
    $configPath = "pywinui.toml"
    if (-not (Test-Path $configPath)) {
        Write-Error "pywinui.toml not found in current directory."
        exit 1
    }
    # Simple TOML parser for flat structure
    $config = @{ project = @{}; app = @{} }
    $currentSection = ""
    foreach ($line in Get-Content $configPath) {
        $line = $line.Trim()
        if ($line -match '^\[(\w+)\]$') {
            $currentSection = $Matches[1]
            if (-not $config.ContainsKey($currentSection)) {
                $config[$currentSection] = @{}
            }
        }
        elseif ($line -match '^(\w+)\s*=\s*"([^"]*)"$') {
            if ($currentSection -and $config.ContainsKey($currentSection)) {
                $config[$currentSection][$Matches[1]] = $Matches[2]
            }
        }
    }
    return $config
}

# ── Dispatch ─────────────────────────────────────────────────────────────

if (-not $Command) {
    Write-Host "WinUIDevKit — Build native WinUI3 desktop apps from any language." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: winuidev <command> [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  setup                         Install Windows App SDK + prerequisites"
    Write-Host "  init <name> [-Language <lang>]  Scaffold a new project"
    Write-Host "  run                            Launch the app in dev mode"
    Write-Host "  build                          Package for distribution"
    Write-Host "  doctor                         Check dependencies"
    Write-Host ""
    Write-Host "Languages: python, rust, go, nodejs, swift"
    exit 0
}

switch ($Command) {
    "setup"  { Invoke-Setup }
    "init"   { Invoke-Init }
    "run"    { Invoke-Run }
    "build"  { Invoke-Build }
    "doctor" { Invoke-Doctor }
}
