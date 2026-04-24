<#
.SYNOPSIS
    Download WinAppSDK .winmd metadata files for Rust binding generation.

.DESCRIPTION
    Fetches the Microsoft.WindowsAppSDK NuGet package and extracts the
    .winmd metadata files into src/rust/metadata/.  These are consumed
    by build.rs via windows-bindgen to generate WinUI 3 Rust bindings.
#>

param(
    [string]$OutputDir = (Join-Path $PSScriptRoot ".." "metadata")
)

$ErrorActionPreference = "Stop"
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) "winuidevkit-nuget"

try {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    New-Item -ItemType Directory -Force -Path $tempDir   | Out-Null

    Write-Host "Downloading Microsoft.WindowsAppSDK NuGet package..."
    nuget install Microsoft.WindowsAppSDK -OutputDirectory $tempDir -NonInteractive | Out-Null

    $winmds = Get-ChildItem -Path $tempDir -Recurse -Filter "*.winmd"
    if ($winmds.Count -eq 0) {
        throw "No .winmd files found in downloaded NuGet packages."
    }

    foreach ($f in $winmds) {
        Copy-Item $f.FullName -Destination $OutputDir -Force
        Write-Host "  Copied $($f.Name)"
    }

    Write-Host "Done — $($winmds.Count) .winmd file(s) in $OutputDir"
}
finally {
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
