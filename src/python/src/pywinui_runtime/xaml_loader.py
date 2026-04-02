"""XAML loader – reads XAML files and creates UI elements via XamlReader."""

import os


class XamlLoadError(RuntimeError):
    """Raised when XAML parsing or loading fails."""


_clr_ready = False


def _ensure_clr():
    """Set up pythonnet with references to Windows App SDK assemblies."""
    global _clr_ready
    if _clr_ready:
        return

    import clr  # type: ignore[import-untyped]

    # Add the NuGet cache DLL directory so assemblies resolve
    try:
        from pywinui.sdk_installer import get_nuget_dll_path

        dll_dir = get_nuget_dll_path()
        if dll_dir:
            import sys

            if dll_dir not in sys.path:
                sys.path.insert(0, dll_dir)
            # Also tell the runtime where to find native DLLs
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(dll_dir)
    except ImportError:
        pass

    try:
        clr.AddReference("Microsoft.UI.Xaml")
    except Exception:
        pass  # May already be loaded or not needed for all paths

    _clr_ready = True


def load_xaml_from_file(xaml_path: str):
    """Load a XAML file and return the root UI element."""
    if not os.path.isfile(xaml_path):
        raise XamlLoadError(f"XAML file not found: {xaml_path}")

    with open(xaml_path, "r", encoding="utf-8") as f:
        xaml_string = f.read()

    return load_xaml_from_string(xaml_string)


def load_xaml_from_string(xaml_string: str):
    """Parse a XAML string and return the root UI element.

    Uses pythonnet to call Microsoft.UI.Xaml.Markup.XamlReader.Load().
    """
    _ensure_clr()

    root = _load_via_pythonnet(xaml_string)
    if root is not None:
        return root

    raise XamlLoadError(
        "Failed to load XAML. Ensure Windows App SDK is installed:\n"
        "  pywinui setup"
    )


def _load_via_pythonnet(xaml_string: str):
    """Load XAML using pythonnet (clr) bindings."""
    try:
        from Microsoft.UI.Xaml.Markup import XamlReader  # type: ignore[import-untyped]

        return XamlReader.Load(xaml_string)
    except Exception:
        return None
    except Exception:
        return None
