<#
.SYNOPSIS
    Discover and install the Windows App SDK runtime.

.DESCRIPTION
    Shared script used by all language packs to:
    - Detect if WinAppSDK MSIX runtime is registered
    - Locate NuGet DLL caches (local + global)
    - Download missing packages via dotnet/winget/direct
    - Populate a local DLL cache for the language pack to consume

.NOTES
    This script is language-agnostic. Each language pack calls it
    during its `setup` command.
#>

param(
    [string]$SdkVersion = "1.8",
    [string]$CacheDir = (Join-Path $env:LOCALAPPDATA "WinUIDevKit\sdk"),
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# ── Constants ────────────────────────────────────────────────────────────

$NuGetSubPackages = @(
    "microsoft.windowsappsdk.foundation"
    "microsoft.windowsappsdk.winui"
    "microsoft.windowsappsdk.interactiveexperiences"
)

$NuGetExtraDeps = @(
    "microsoft.windows.cswinrt"
    "microsoft.windows.sdk.net.ref"
)

$RequiredDlls = @(
    "Microsoft.WindowsAppRuntime.Bootstrap.Net.dll"
    "WinRT.Runtime.dll"
    "Microsoft.Windows.SDK.NET.dll"
    "Microsoft.InteractiveExperiences.Projection.dll"
    "Microsoft.WinUI.dll"
)

# ── Detection ────────────────────────────────────────────────────────────

function Test-MsixRuntime {
    try {
        $pkgs = Get-AppxPackage -Name "Microsoft.WindowsAppRuntime*" 2>$null
        $match = $pkgs | Where-Object { $_.Version -like "$SdkVersion.*" }
        return $null -ne $match
    } catch {
        return $false
    }
}

function Get-NuGetGlobalCache {
    $cache = Join-Path $env:USERPROFILE ".nuget\packages"
    if (Test-Path $cache) { return $cache }
    return $null
}

function Find-BestVersionDir {
    param([string]$PackageDir, [string]$MajorMinor)

    if (-not (Test-Path $PackageDir)) { return $null }
    $dirs = Get-ChildItem $PackageDir -Directory |
        Where-Object { $_.Name -like "$MajorMinor.*" } |
        Sort-Object { [version]$_.Name } -Descending
    if ($dirs) { return $dirs[0].FullName }
    return $null
}

# ── Population ───────────────────────────────────────────────────────────

function Install-SdkCache {
    $targetDir = Join-Path $CacheDir "lib"
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    }

    $nugetCache = Get-NuGetGlobalCache
    if (-not $nugetCache) {
        Write-Warning "NuGet global cache not found at ~/.nuget/packages"
        return $false
    }

    $found = 0

    # Scan sub-packages (foundation, winui, interactiveexperiences)
    foreach ($pkg in $NuGetSubPackages) {
        $pkgDir = Join-Path $nugetCache $pkg
        $versionDir = Find-BestVersionDir $pkgDir $SdkVersion
        if ($versionDir) {
            $libDir = Join-Path $versionDir "lib\net8.0-windows10.0.26100.0"
            if (-not (Test-Path $libDir)) {
                $libDir = Get-ChildItem (Join-Path $versionDir "lib") -Directory -Filter "net*" |
                    Select-Object -First 1 -ExpandProperty FullName
            }
            if ($libDir -and (Test-Path $libDir)) {
                Get-ChildItem $libDir -Filter "*.dll" | ForEach-Object {
                    Copy-Item $_.FullName $targetDir -Force
                    $found++
                }
            }
        }
    }

    # Scan extra deps (cswinrt, sdk.net.ref)
    foreach ($pkg in $NuGetExtraDeps) {
        $pkgDir = Join-Path $nugetCache $pkg
        if (Test-Path $pkgDir) {
            $versionDir = Get-ChildItem $pkgDir -Directory |
                Sort-Object { try { [version]$_.Name } catch { [version]"0.0" } } -Descending |
                Select-Object -First 1 -ExpandProperty FullName
            if ($versionDir) {
                Get-ChildItem $versionDir -Recurse -Filter "*.dll" | ForEach-Object {
                    Copy-Item $_.FullName $targetDir -Force
                    $found++
                }
            }
        }
    }

    if ($Verbose) { Write-Host "Copied $found DLLs to $targetDir" }

    # Verify required DLLs
    $missing = $RequiredDlls | Where-Object { -not (Test-Path (Join-Path $targetDir $_)) }
    if ($missing) {
        Write-Warning "Missing DLLs: $($missing -join ', ')"
        return $false
    }

    # Create runtimeconfig.json for .NET CoreCLR
    $rcPath = Join-Path $targetDir "winuidevkit.runtimeconfig.json"
    if (-not (Test-Path $rcPath)) {
        @{
            runtimeOptions = @{
                tfm = "net8.0"
                frameworks = @(
                    @{ name = "Microsoft.WindowsDesktop.App"; version = "8.0.0" }
                )
            }
        } | ConvertTo-Json -Depth 4 | Set-Content $rcPath -Encoding utf8
    }

    return $true
}

# ── Entry Point ──────────────────────────────────────────────────────────

function Invoke-Setup {
    Write-Host "WinUIDevKit SDK Setup (v$SdkVersion)" -ForegroundColor Cyan
    Write-Host "=" * 40

    # Check MSIX runtime
    $msix = Test-MsixRuntime
    if ($msix) {
        Write-Host "  MSIX Runtime: installed" -ForegroundColor Green
    } else {
        Write-Host "  MSIX Runtime: not found" -ForegroundColor Yellow
    }

    # Populate DLL cache
    $ok = Install-SdkCache
    if ($ok) {
        Write-Host "  DLL Cache:    ready ($CacheDir)" -ForegroundColor Green
    } else {
        Write-Host "  DLL Cache:    incomplete" -ForegroundColor Red
    }

    Write-Host "=" * 40
    return $ok
}

# Run if executed directly
if ($MyInvocation.InvocationName -ne '.') {
    $result = Invoke-Setup
    if (-not $result) { exit 1 }
}
