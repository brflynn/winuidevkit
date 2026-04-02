"""pywinui_runtime – Runtime core for WinUI3 + Python apps."""

# CoreCLR must be loaded before any `import clr` in the process.
from pywinui_runtime.bootstrap import ensure_coreclr as _ensure_coreclr
_ensure_coreclr()

from pywinui_runtime.app import App, window
from pywinui_runtime.bootstrap import ensure_windows_app_runtime

__all__ = ["App", "window", "ensure_windows_app_runtime"]
