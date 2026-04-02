"""Windows App Runtime bootstrap initialisation.

Handles three scenarios:
1. Managed bootstrap via pythonnet (.NET CoreCLR) – most reliable for unpackaged apps
2. Native bootstrap DLL via ctypes – fallback
3. Auto-install if nothing found

IMPORTANT: ``ensure_coreclr()`` must be called before any ``import clr``
statement because pythonnet locks the runtime choice on first import.
"""

import ctypes
import json
import os
import sys


_PACKAGE_VERSION_MIN = (1, 0, 0, 0)
_SDK_MAJOR_MINOR = 0x00010008  # 1.8

# Assemblies that must be loaded (in order) for the WinUI3 projection.
_REQUIRED_ASSEMBLIES = [
    "Microsoft.WindowsAppRuntime.Bootstrap.Net",
    "WinRT.Runtime",
    "Microsoft.Windows.SDK.NET",
    "Microsoft.InteractiveExperiences.Projection",
    "Microsoft.WinUI",
]

_bootstrapped = False
_coreclr_loaded = False


class BootstrapError(RuntimeError):
    """Raised when Windows App Runtime bootstrap fails."""


def ensure_coreclr():
    """Load pythonnet with the CoreCLR (.NET 8+) runtime.

    Must be called *before* any ``import clr`` in the process.
    WinUI3 projection assemblies require .NET 5+ (``IDynamicInterfaceCastable``).
    """
    global _coreclr_loaded
    if _coreclr_loaded:
        return

    try:
        from pythonnet import load as _load_runtime  # type: ignore[import-untyped]

        rc_path = _get_or_create_runtimeconfig()
        if rc_path:
            _load_runtime("coreclr", runtime_config=rc_path)
        else:
            _load_runtime("coreclr")
        _coreclr_loaded = True
    except Exception:
        # If coreclr load fails (e.g. already loaded), just proceed
        _coreclr_loaded = True


def _get_or_create_runtimeconfig() -> str | None:
    """Return path to a runtimeconfig.json targeting .NET 8 WindowsDesktop."""
    try:
        from pywinui.sdk_installer import get_nuget_dll_path
        dll_dir = get_nuget_dll_path()
        if dll_dir:
            rc_path = os.path.join(dll_dir, "pywinui.runtimeconfig.json")
            if not os.path.isfile(rc_path):
                rc = {
                    "runtimeOptions": {
                        "tfm": "net8.0",
                        "framework": {
                            "name": "Microsoft.WindowsDesktop.App",
                            "version": "8.0.0",
                        },
                    }
                }
                with open(rc_path, "w") as f:
                    json.dump(rc, f, indent=2)
            return rc_path
    except ImportError:
        pass
    return None


def ensure_windows_app_runtime():
    """Initialise the Windows App Runtime.

    Tries in order:
    1. Switch pythonnet to CoreCLR (required for WinUI3 projection).
    2. Managed bootstrap via pythonnet (most reliable for unpackaged apps).
    3. Native bootstrap DLL from system or NuGet cache.
    4. Auto-install the SDK, then retry.
    """
    global _bootstrapped
    if _bootstrapped:
        return

    if sys.platform != "win32":
        raise BootstrapError("pywinui requires Windows 10 1809+ (x64).")

    # Must load CoreCLR before any clr import
    ensure_coreclr()

    # Attempt 1: Managed .NET bootstrap (preferred)
    if _try_managed_bootstrap():
        _bootstrapped = True
        return

    # Attempt 2: Native ctypes bootstrap
    dll = _try_load_bootstrap_dll() or _try_load_from_cache()
    if dll is not None:
        _call_native_bootstrap(dll)
        _bootstrapped = True
        return

    # Attempt 3: Auto-install
    print("[pywinui] Windows App SDK not found. Running automatic setup...",
          file=sys.stderr)
    try:
        from pywinui.sdk_installer import install_sdk
        install_sdk(verbose=True, interactive=False)
    except Exception as exc:
        _fail_with_diagnostic(
            f"Auto-install failed: {exc}\n"
            "Run manually:  pywinui setup"
        )

    # Retry managed bootstrap first
    if _try_managed_bootstrap():
        _bootstrapped = True
        return

    # Retry native
    dll = _try_load_bootstrap_dll() or _try_load_from_cache()
    if dll is not None:
        _call_native_bootstrap(dll)
        _bootstrapped = True
        return

    _fail_with_diagnostic(
        "Windows App SDK could not be loaded after installation.\n"
        "Try running:  pywinui setup\n"
        "Or install manually:\n"
        "  https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/downloads"
    )


def shutdown_bootstrap():
    """Shut down the bootstrap if it was initialized."""
    global _bootstrapped
    if not _bootstrapped:
        return

    # Try managed shutdown
    try:
        import clr  # type: ignore[import-untyped]
        from Microsoft.Windows.ApplicationModel.DynamicDependency import Bootstrap  # type: ignore
        Bootstrap.Shutdown()
        _bootstrapped = False
        return
    except Exception:
        pass

    # Native shutdown fallback
    try:
        dll = _try_load_bootstrap_dll() or _try_load_from_cache()
        if dll:
            dll.MddBootstrapShutdown()
    except OSError:
        pass
    _bootstrapped = False


# ── Managed .NET bootstrap (preferred) ───────────────────────────────────

def _try_managed_bootstrap() -> bool:
    """Use pythonnet to call the managed Bootstrap.Initialize().

    This is the most reliable path for unpackaged desktop apps because
    the managed API handles DDLM resolution, version matching, and
    framework package activation internally.
    """
    try:
        import clr  # type: ignore[import-untyped]
    except ImportError:
        return False

    # Add NuGet cache DLLs to the assembly search path
    dll_dir = _add_nuget_cache_to_path()
    if not dll_dir:
        return False

    # Load the full assembly chain required for WinUI3
    for asm_name in _REQUIRED_ASSEMBLIES:
        try:
            clr.AddReference(asm_name)
        except Exception:
            # Try by full path
            full_path = os.path.join(dll_dir, asm_name + ".dll")
            if os.path.isfile(full_path):
                try:
                    clr.AddReference(full_path)
                except Exception:
                    return False
            else:
                return False

    try:
        from Microsoft.Windows.ApplicationModel.DynamicDependency import Bootstrap  # type: ignore

        Bootstrap.Initialize(_SDK_MAJOR_MINOR)
        return True
    except Exception:
        try:
            from Microsoft.Windows.ApplicationModel.DynamicDependency import Bootstrap  # type: ignore
            result = Bootstrap.TryInitialize(_SDK_MAJOR_MINOR)
            if result:
                return True
        except Exception:
            pass
        return False


def _add_nuget_cache_to_path() -> str | None:
    """Add the pywinui NuGet cache directory to both sys.path and DLL search.

    Returns the DLL directory path if found, None otherwise.
    """
    try:
        from pywinui.sdk_installer import get_nuget_dll_path

        dll_dir = get_nuget_dll_path()
        if dll_dir:
            if dll_dir not in sys.path:
                sys.path.insert(0, dll_dir)
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(dll_dir)
            return dll_dir
    except ImportError:
        pass
    return None


def _find_managed_bootstrap_dll() -> str | None:
    """Locate the managed bootstrap DLL."""
    try:
        from pywinui.sdk_installer import get_nuget_dll_path
        dll_dir = get_nuget_dll_path()
        if dll_dir:
            path = os.path.join(dll_dir, "Microsoft.WindowsAppRuntime.Bootstrap.Net.dll")
            if os.path.isfile(path):
                return path
    except ImportError:
        pass
    return None


# ── Native ctypes bootstrap (fallback) ──────────────────────────────────

def _try_load_bootstrap_dll():
    """Try loading the native bootstrap DLL from the system search path."""
    try:
        return ctypes.WinDLL("Microsoft.WindowsAppRuntime.Bootstrap.dll")
    except OSError:
        return None


def _try_load_from_cache():
    """Try loading the native bootstrap DLL from the pywinui NuGet cache."""
    try:
        from pywinui.sdk_installer import get_nuget_dll_path
    except ImportError:
        return None

    dll_dir = get_nuget_dll_path()
    if dll_dir is None:
        return None

    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(dll_dir)

    bootstrap_path = os.path.join(
        dll_dir, "Microsoft.WindowsAppRuntime.Bootstrap.dll"
    )
    if not os.path.isfile(bootstrap_path):
        return None

    try:
        return ctypes.WinDLL(bootstrap_path)
    except OSError:
        return None


def _call_native_bootstrap(dll):
    """Call MddBootstrapInitialize2 via ctypes.

    Signature: HRESULT MddBootstrapInitialize2(
        UINT32 majorMinorVersion,
        PCWSTR versionTag,
        PACKAGE_VERSION minVersion    // UINT64
    )
    """
    min_version = _pack_version(*_PACKAGE_VERSION_MIN)

    func = dll.MddBootstrapInitialize2
    func.argtypes = [ctypes.c_uint32, ctypes.c_wchar_p, ctypes.c_uint64]
    func.restype = ctypes.c_int32  # HRESULT

    try:
        hr = func(_SDK_MAJOR_MINOR, "", min_version)
    except Exception as exc:
        _fail_with_diagnostic(f"Bootstrap call failed: {exc}")
        return

    if hr != 0:
        _fail_with_diagnostic(
            f"MddBootstrapInitialize2 returned HRESULT 0x{hr & 0xFFFFFFFF:08X}.\n"
            "The Windows App Runtime may be partially installed.\n"
            "Try:  pywinui setup"
        )


def _pack_version(major: int, minor: int, build: int, revision: int) -> int:
    """Pack a PACKAGE_VERSION into a 64-bit integer."""
    return (major << 48) | (minor << 32) | (build << 16) | revision


def _fail_with_diagnostic(message: str):
    print(f"\n[pywinui] Bootstrap Error\n{'=' * 40}", file=sys.stderr)
    print(message, file=sys.stderr)
    print("=" * 40, file=sys.stderr)
    raise SystemExit(1)
