"""Windows App SDK installer – downloads and installs the WinUI3 runtime.

This module handles automatic provisioning of the Windows App SDK runtime
so developers don't need to manually install it. Called by:
  - ``pywinui setup`` (explicit)
  - ``pywinui run`` (auto-detects and prompts)

Installation strategy (in priority order):
  1. ``winget install`` – cleanest path, handles runtime + deps
  2. ``dotnet restore`` – pulls NuGet package for managed DLLs
  3. Direct HTTP download – fallback if winget/dotnet unavailable
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request

# Windows App SDK 1.8 (stable)
_SDK_VERSION = "1.8"
_WINGET_ID = "Microsoft.WindowsAppSDK." + _SDK_VERSION

# In WinAppSDK 1.8 the NuGet meta-package (Microsoft.WindowsAppSDK) is
# split into sub-packages.  The bootstrap DLL lives in the *foundation*
# package and the WinUI XAML DLLs live in the *winui* package.
_NUGET_SUB_PACKAGES = [
    # (package-id-lowercase, preferred-version-prefix)
    ("microsoft.windowsappsdk.foundation", "1.8."),
    ("microsoft.windowsappsdk.winui",      "1.8."),
    ("microsoft.windowsappsdk.interactiveexperiences", "1.8."),
]
# Additional dependencies not from WindowsAppSDK but needed for the projection
_NUGET_EXTRA_DEPS = [
    # (package-id-lowercase, version-prefix, sub-dir-to-scan)
    ("microsoft.windows.cswinrt",       "2.",    "lib/net8.0"),
    ("microsoft.windows.sdk.net.ref",   "10.0.", "lib/net8.0"),
]
# Fallback: also try the old all-in-one meta-package for older layouts
_NUGET_LEGACY_PACKAGE = "microsoft.windowsappsdk"

# Direct download fallback
_INSTALLER_URLS = {
    "x64": (
        f"https://aka.ms/windowsappsdk/{_SDK_VERSION}/windowsappruntimeinstall-x64.exe",
        "windowsappruntimeinstall-x64.exe",
    ),
    "arm64": (
        f"https://aka.ms/windowsappsdk/{_SDK_VERSION}/windowsappruntimeinstall-arm64.exe",
        "windowsappruntimeinstall-arm64.exe",
    ),
}


class SetupError(RuntimeError):
    """Raised when SDK installation fails."""


def is_sdk_installed() -> bool:
    """Check whether the Windows App SDK runtime is available."""
    if sys.platform != "win32":
        return False

    # Check for registered MSIX framework packages (most reliable on modern Windows)
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-AppxPackage -Name 'MicrosoftCorporationII.WinAppRuntime.Main.{_SDK_VERSION}' "
             "| Select-Object -First 1 -ExpandProperty Version"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return True
    except Exception:
        pass

    import ctypes

    try:
        ctypes.WinDLL("Microsoft.WindowsAppRuntime.Bootstrap.dll")
        return True
    except OSError:
        pass

    return False


def get_nuget_dll_path() -> str | None:
    """Return the path to the cached WinAppSDK NuGet package DLLs.

    Returns None if the NuGet package is not yet downloaded.
    """
    # Try every 1.8.x cache directory (newest first)
    base = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "pywinui", "sdk",
    )
    if not os.path.isdir(base):
        return None

    for ver_dir in sorted(os.listdir(base), reverse=True):
        if not ver_dir.startswith(_SDK_VERSION + "."):
            continue
        dll_dir = os.path.join(base, ver_dir, "lib")
        bootstrap = os.path.join(dll_dir, "Microsoft.WindowsAppRuntime.Bootstrap.Net.dll")
        if os.path.isfile(bootstrap):
            return dll_dir
    return None


def install_sdk(verbose: bool = True, interactive: bool = True) -> bool:
    """Download and install the Windows App SDK runtime + NuGet package.

    Strategy:
      1. Scan local NuGet cache (zero network, fastest)
      2. winget install (handles runtime + MSIX packages)
      3. dotnet restore (pulls NuGet DLLs for pythonnet)
      4. Direct download fallback

    Returns True on success.
    """
    if sys.platform != "win32":
        raise SetupError("pywinui requires Windows.")

    arch = _get_arch()

    if verbose:
        print(f"[pywinui] Setting up Windows App SDK {_SDK_VERSION} ({arch})...")
        print()

    # Step 1: Try to populate cache from local NuGet packages (no network)
    nuget_ok = _populate_from_local_nuget_cache(arch, verbose=verbose)

    # Step 2: Install the runtime (if not already registered)
    runtime_ok = is_sdk_installed()
    if runtime_ok and verbose:
        print("  [1/3] Runtime already available.")

    if not runtime_ok:
        # Try winget first (cleanest path)
        if _has_command("winget"):
            runtime_ok = _install_via_winget(verbose=verbose)

        # Fallback: direct download
        if not runtime_ok and arch in _INSTALLER_URLS:
            runtime_ok = _install_via_download(arch, verbose=verbose)

    # Step 2b: Get NuGet managed DLLs (needed for pythonnet interop)
    if not nuget_ok:
        # Try dotnet restore
        if _has_command("dotnet"):
            nuget_ok = _install_nuget_via_dotnet(verbose=verbose)

    # Fallback: direct NuGet download
    if not nuget_ok:
        try:
            _download_nuget_package(verbose=verbose)
            nuget_ok = True
        except Exception as exc:
            if verbose:
                print(f"  NuGet download failed: {exc}")

    # Step 3: Ensure pythonnet
    _ensure_pythonnet(verbose=verbose)

    if verbose:
        print()
        if runtime_ok and nuget_ok:
            print("[pywinui] Windows App SDK setup complete.")
        elif nuget_ok:
            print("[pywinui] NuGet DLLs ready. Runtime may need admin install.")
            print("  Try: winget install Microsoft.WindowsAppSDK.1.5")
        else:
            print("[pywinui] Setup had issues. See messages above.")

    return runtime_ok or nuget_ok


# ── Installation strategies ──────────────────────────────────────────────

def _populate_from_local_nuget_cache(arch: str, verbose: bool) -> bool:
    """Copy DLLs from the local NuGet global-packages cache (no network).

    In WinAppSDK 1.8 the packages are split:
      - microsoft.windowsappsdk.foundation  → bootstrap + runtime managed DLLs
      - microsoft.windowsappsdk.winui        → WinUI XAML managed DLLs
    We scan both and copy everything into a single flat ``lib/`` directory.
    """
    nuget_home = _get_nuget_global_packages()

    # Resolve each sub-package to a concrete directory
    resolved: list[tuple[str, str]] = []  # [(pkg_id, abs_path), ...]
    for pkg_id, ver_prefix in _NUGET_SUB_PACKAGES:
        pkg_base = os.path.join(nuget_home, pkg_id)
        pkg_dir = _find_best_version_dir(pkg_base, ver_prefix)
        if pkg_dir:
            resolved.append((pkg_id, pkg_dir))
            if verbose:
                print(f"  [cache] Found {pkg_id} → {os.path.basename(pkg_dir)}")

    # Fallback: try old all-in-one meta-package
    if not resolved:
        pkg_base = os.path.join(nuget_home, _NUGET_LEGACY_PACKAGE)
        pkg_dir = _find_best_version_dir(pkg_base, _SDK_VERSION + ".")
        if pkg_dir:
            resolved.append((_NUGET_LEGACY_PACKAGE, pkg_dir))
            if verbose:
                print(f"  [cache] Found legacy package → {os.path.basename(pkg_dir)}")

    if not resolved:
        if verbose:
            print(f"  [cache] No {_SDK_VERSION}.x packages in local NuGet cache.")
        return False

    # Use the foundation version for the cache directory name
    foundation_ver = None
    for pid, pdir in resolved:
        if "foundation" in pid:
            foundation_ver = os.path.basename(pdir)
            break
    if foundation_ver is None:
        foundation_ver = os.path.basename(resolved[0][1])

    cache_dir = _get_cache_dir(foundation_ver)
    lib_dir = os.path.join(cache_dir, "lib")

    # Already cached?
    marker = os.path.join(lib_dir, ".version")
    if os.path.isfile(marker):
        with open(marker) as f:
            cached_ver = f.read().strip()
        if cached_ver == foundation_ver:
            if verbose:
                print("  [cache] NuGet DLLs already cached.")
            return True

    if verbose:
        print(f"  [cache] Copying DLLs from local NuGet cache...")

    os.makedirs(lib_dir, exist_ok=True)
    copied = 0

    for _, pkg_dir in resolved:
        for walk_root, _dirs, files in os.walk(pkg_dir):
            for fname in files:
                if not fname.endswith((".dll", ".pri", ".winmd")):
                    continue
                src = os.path.join(walk_root, fname)
                if os.path.getsize(src) < 1024:
                    continue
                rel = walk_root.replace(pkg_dir, "").replace("\\", "/").lower()
                if any(target in rel for target in [
                    f"runtimes/win-{arch}/native",
                    "lib/net6.0",
                    "lib/net8.0",
                    "lib/uap10.0",
                ]):
                    dst = os.path.join(lib_dir, fname)
                    shutil.copy2(src, dst)
                    copied += 1

    # Also copy extra dependencies (CsWinRT runtime, Windows SDK .NET projection)
    for pkg_id, ver_prefix, scan_dir in _NUGET_EXTRA_DEPS:
        pkg_base = os.path.join(nuget_home, pkg_id)
        pkg_dir = _find_best_version_dir(pkg_base, ver_prefix)
        if not pkg_dir:
            continue
        target_dir = os.path.join(pkg_dir, *scan_dir.split("/"))
        if not os.path.isdir(target_dir):
            continue
        if verbose:
            print(f"  [cache] Found {pkg_id} → {os.path.basename(pkg_dir)}")
        for fname in os.listdir(target_dir):
            if not fname.endswith(".dll"):
                continue
            src = os.path.join(target_dir, fname)
            if os.path.getsize(src) < 1024:
                continue
            dst = os.path.join(lib_dir, fname)
            shutil.copy2(src, dst)
            copied += 1

    if copied > 0:
        with open(marker, "w") as f:
            f.write(foundation_ver)
        if verbose:
            print(f"        Cached {copied} DLLs in {lib_dir}")
        return True

    if verbose:
        print("        No usable DLLs found in local cache.")
    return False


def _find_best_version_dir(pkg_base: str, ver_prefix: str) -> str | None:
    """Return the newest version directory under *pkg_base* matching *ver_prefix*."""
    if not os.path.isdir(pkg_base):
        return None
    candidates = [
        v for v in sorted(os.listdir(pkg_base), reverse=True)
        if v.startswith(ver_prefix) and not v.endswith("-experimental")
    ]
    for v in candidates:
        full = os.path.join(pkg_base, v)
        if os.path.isdir(full):
            return full
    return None


def _install_via_winget(verbose: bool) -> bool:
    """Install Windows App SDK runtime via winget."""
    if verbose:
        print("  [1/3] Installing runtime via winget...")

    try:
        result = subprocess.run(
            [
                "winget", "install",
                "--id", _WINGET_ID,
                "--accept-source-agreements",
                "--accept-package-agreements",
                "--silent",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            if verbose:
                print("        Runtime installed successfully.")
            return True
        elif "already installed" in result.stdout.lower():
            if verbose:
                print("        Runtime already installed.")
            return True
        else:
            if verbose:
                print(f"        winget returned code {result.returncode}")
                if result.stderr.strip():
                    for line in result.stderr.strip().splitlines()[:3]:
                        print(f"        {line}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        if verbose:
            print(f"        winget failed: {exc}")
        return False


def _install_via_download(arch: str, verbose: bool) -> bool:
    """Download and run the WindowsAppRuntime installer exe."""
    url, filename = _INSTALLER_URLS[arch]
    cache_dir = _get_cache_dir()
    installer_path = os.path.join(cache_dir, filename)

    if verbose:
        print(f"  [1/3] Downloading {filename}...")

    try:
        if not os.path.isfile(installer_path):
            _download_file(url, installer_path)

        if verbose:
            print(f"        Running installer (may request admin)...")

        result = subprocess.run(
            [installer_path, "--quiet"],
            capture_output=True,
            timeout=300,
        )
        if result.returncode in (0, 3010):
            if verbose:
                print("        Runtime installed successfully.")
            return True
        else:
            if verbose:
                print(f"        Installer returned code {result.returncode}")
                print("        You may need to run as Administrator:")
                print(f"          {installer_path} --quiet")
            return False
    except Exception as exc:
        if verbose:
            print(f"        Download/install failed: {exc}")
        return False


def _install_nuget_via_dotnet(verbose: bool) -> bool:
    """Use ``dotnet restore`` to pull the NuGet meta-package (which brings in sub-packages)."""
    if verbose:
        print("  [2/3] Restoring NuGet packages via dotnet...")

    cache_dir = _get_cache_dir()

    # Create a temp project that references the meta-package (it pulls foundation + winui)
    proj_dir = os.path.join(cache_dir, "_restore")
    os.makedirs(proj_dir, exist_ok=True)
    proj_file = os.path.join(proj_dir, "restore.csproj")
    with open(proj_file, "w") as f:
        f.write("""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>
    <OutputType>Library</OutputType>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.WindowsAppSDK" Version="1.8.*" />
  </ItemGroup>
</Project>
""")

    try:
        result = subprocess.run(
            ["dotnet", "restore", proj_file],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            if verbose:
                print(f"        dotnet restore failed (code {result.returncode})")
                for line in result.stderr.strip().splitlines()[:3]:
                    print(f"        {line}")
            return False
    except Exception as exc:
        if verbose:
            print(f"        dotnet restore failed: {exc}")
        return False

    # After restore the sub-packages are in the NuGet cache — delegate to the cache scanner
    arch = _get_arch()
    return _populate_from_local_nuget_cache(arch, verbose=verbose)


def _download_nuget_package(verbose: bool) -> str:
    """Download the NuGet sub-packages directly via HTTP (fallback)."""
    # Try downloading the two sub-packages individually
    cache_dir = _get_cache_dir()
    lib_dir = os.path.join(cache_dir, "lib")
    os.makedirs(lib_dir, exist_ok=True)
    arch = _get_arch()

    if verbose:
        print("  [2/3] Downloading NuGet packages (direct)...")

    import zipfile

    for pkg_id, ver_prefix in _NUGET_SUB_PACKAGES:
        nupkg_url = f"https://www.nuget.org/api/v2/package/{pkg_id}"
        nupkg_path = os.path.join(cache_dir, f"{pkg_id}.nupkg")

        if verbose:
            print(f"        Downloading {pkg_id}...")
        _download_file(nupkg_url, nupkg_path)

        with zipfile.ZipFile(nupkg_path) as zf:
            for member in zf.namelist():
                if member.endswith((".dll", ".pri", ".winmd")):
                    if ("lib/net" in member or
                            f"runtimes/win-{arch}/native" in member):
                        _extract_flat(zf, member, lib_dir)

    # Write a version marker
    marker = os.path.join(lib_dir, ".version")
    with open(marker, "w") as f:
        f.write(_SDK_VERSION + ".downloaded")

    if verbose:
        print(f"        NuGet DLLs cached in {lib_dir}")

    return lib_dir


def _ensure_pythonnet(verbose: bool):
    """Install pythonnet if not already available."""
    try:
        import clr  # type: ignore[import-untyped]

        if verbose:
            print("  [3/3] pythonnet already installed.")
        return
    except ImportError:
        pass

    if verbose:
        print("  [3/3] Installing pythonnet...")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pythonnet>=3.0.3"],
        capture_output=not verbose,
        check=True,
    )

    if verbose:
        print("  pythonnet installed.")


# ── helpers ──────────────────────────────────────────────────────────────

def _get_cache_dir(version: str | None = None) -> str:
    """Return the pywinui SDK cache directory for *version*.

    If *version* is None, uses the newest available 1.8.x cache or
    falls back to a default placeholder name.
    """
    base = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "pywinui", "sdk",
    )
    if version is None:
        # Pick newest existing 1.8.x cache dir
        if os.path.isdir(base):
            for d in sorted(os.listdir(base), reverse=True):
                if d.startswith(_SDK_VERSION + "."):
                    version = d
                    break
        if version is None:
            version = _SDK_VERSION + ".0"  # placeholder until resolved
    cache = os.path.join(base, version)
    os.makedirs(cache, exist_ok=True)
    return cache


def _get_arch() -> str:
    """Return 'x64' or 'arm64'."""
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64", "x64"):
        return "x64"
    if machine in ("arm64", "aarch64"):
        return "arm64"
    return machine


def _has_command(name: str) -> bool:
    """Check whether a CLI tool is available."""
    return shutil.which(name) is not None


def _get_nuget_global_packages() -> str:
    """Return the NuGet global-packages cache directory."""
    # dotnet nuget locals global-packages --list
    try:
        result = subprocess.run(
            ["dotnet", "nuget", "locals", "global-packages", "--list"],
            capture_output=True, text=True, timeout=15,
        )
        for line in result.stdout.splitlines():
            if "global-packages" in line.lower():
                # Format: "global-packages: C:\Users\...\.nuget\packages"
                _, _, path = line.partition(":")
                path = path.strip()
                if os.path.isdir(path):
                    return path
    except Exception:
        pass

    # Fallback: default location
    return os.path.join(os.path.expanduser("~"), ".nuget", "packages")


def _download_file(url: str, dest: str):
    """Download a URL to a local file with progress."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".tmp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pywinui-setup/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as f:
            total = resp.headers.get("Content-Length")
            downloaded = 0
            chunk_size = 256 * 1024
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // int(total)
                    print(f"\r    {pct}% ({downloaded // 1024}KB)", end="", flush=True)
            if total:
                print()  # newline after progress
        shutil.move(tmp, dest)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _extract_flat(zf, member: str, dest_dir: str):
    """Extract a zip member into dest_dir with a flat filename."""
    filename = os.path.basename(member)
    if not filename:
        return
    dest = os.path.join(dest_dir, filename)
    with zf.open(member) as src, open(dest, "wb") as dst:
        shutil.copyfileobj(src, dst)
