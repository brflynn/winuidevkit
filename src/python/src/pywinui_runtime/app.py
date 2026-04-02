"""App – high-level entry point for running a pywinui WinUI3 application."""

import importlib
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any

from pywinui_runtime.bootstrap import ensure_windows_app_runtime, ensure_coreclr, shutdown_bootstrap
from pywinui_runtime.binder import bind_xaml, wire_events, ViewProxy


class App:
    """Main application class for pywinui apps."""

    @staticmethod
    def run(xaml: str, codebehind: str | None = None):
        """Bootstrap the runtime, load XAML, wire code-behind, and start the app loop.

        Parameters
        ----------
        xaml:
            Relative path to the XAML file (e.g. ``"app/MainWindow.xaml"``).
        codebehind:
            Optional dotted-path to code-behind class in
            ``module.path:ClassName`` format.
            Can also be a class type directly (when using the @window decorator).
        """
        # 1. Bootstrap Windows App Runtime
        ensure_windows_app_runtime()

        # 2. Read XAML and extract window metadata + inner content
        xaml_path = os.path.abspath(xaml)
        with open(xaml_path, "r", encoding="utf-8") as f:
            xaml_string = f.read()

        title, content_xaml = _extract_window_content(xaml_string)

        # 3. Start the WinUI3 application (blocks until app exits)
        import clr  # type: ignore[import-untyped]

        # Ensure NuGet DLL cache is on the search path for assembly resolution
        _add_assembly_search_paths()

        _add_reference_safe("Microsoft.WinUI")
        from Microsoft.UI.Xaml import Application, ApplicationInitializationCallback  # type: ignore

        # Store state for the launch callback
        _launch_state = {
            "xaml_string": xaml_string,
            "content_xaml": content_xaml,
            "title": title or "pywinui App",
            "codebehind": codebehind,
        }

        def _on_launched(p):
            _do_launch(_launch_state)

        try:
            callback = ApplicationInitializationCallback(_on_launched)
            Application.Start(callback)
        finally:
            shutdown_bootstrap()


def _do_launch(state: dict):
    """Called inside Application.Start — creates window, loads XAML, wires events."""
    from Microsoft.UI.Xaml import Window  # type: ignore
    from Microsoft.UI.Xaml.Markup import XamlReader  # type: ignore

    window = Window()
    window.Title = state["title"]

    content_xaml = state["content_xaml"]
    if content_xaml:
        content = XamlReader.Load(content_xaml)
        window.Content = content
    else:
        content = window

    # Build view proxy from the content tree
    view = bind_xaml(content, state["xaml_string"])

    # Instantiate code-behind
    codebehind = state["codebehind"]
    cb_instance = None
    if isinstance(codebehind, type):
        cb_instance = codebehind(view)
    elif codebehind:
        cb_instance = _instantiate_codebehind(codebehind, view)

    # Auto-wire events
    if cb_instance is not None:
        wire_events(view, cb_instance)

    window.Activate()


def _extract_window_content(xaml_string: str) -> tuple[str | None, str | None]:
    """Extract the Title and inner content from a ``<Window>`` XAML document.

    If the root element is a ``<Window>``, returns ``(title, inner_content_xaml)``
    where *inner_content_xaml* is a standalone XAML fragment containing just the
    window's child content (with the necessary xmlns declarations).

    If the root is NOT a Window, returns ``(None, xaml_string)`` unchanged.
    """
    try:
        root = ET.fromstring(xaml_string)
    except ET.ParseError:
        return None, xaml_string

    # Check if root tag is Window (strip namespace prefix)
    tag = root.tag
    if "}" in tag:
        tag = tag.split("}", 1)[1]

    if tag != "Window":
        return None, xaml_string

    title = root.attrib.get("Title")

    # The inner content is the first child element of <Window>
    children = list(root)
    if not children:
        return title, None

    child = children[0]

    # Rebuild the inner content as standalone XAML with xmlns declarations
    # Collect all namespace declarations from the original XAML
    import re
    ns_decls = re.findall(r'xmlns(?::\w+)?="[^"]*"', xaml_string)
    ns_str = " ".join(ns_decls)

    # Serialize the child element
    inner = ET.tostring(child, encoding="unicode")

    # Inject xmlns declarations into the root element of the inner XAML
    # The inner element needs the namespace declarations to be valid
    if ns_str:
        # Find the first '>' or ' ' in the inner xml to inject namespaces
        match = re.match(r"(<\S+)", inner)
        if match:
            inner = match.group(1) + " " + ns_str + inner[match.end():]

    return title, inner


def window(xaml: str):
    """Decorator that turns a class into a runnable pywinui window.

    Usage (complete app in 5 lines)::

        from pywinui_runtime import window

        @window("MainWindow.xaml")
        class MainWindow:
            def __init__(self, view):
                self.view = view

            def on_myButton_Click(self, sender, args):
                sender.Content = "Clicked!"

        # Then just:  MainWindow.run()

    """
    def decorator(cls):
        cls._pywinui_xaml = xaml

        @staticmethod
        def _run():
            App.run(xaml=cls._pywinui_xaml, codebehind=cls)

        cls.run = _run
        return cls

    return decorator


def _instantiate_codebehind(spec: str, view: ViewProxy) -> Any:
    """Import and instantiate the code-behind class.

    ``spec`` is ``"module.path:ClassName"``.
    """
    if ":" not in spec:
        raise ValueError(
            f"codebehind must be 'module.path:ClassName', got '{spec}'"
        )

    module_path, class_name = spec.rsplit(":", 1)

    # Ensure the current directory is on sys.path so local imports work
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(view)


def _add_assembly_search_paths():
    """Add the pywinui NuGet DLL cache to pythonnet's assembly search path."""
    try:
        from pywinui.sdk_installer import get_nuget_dll_path

        dll_dir = get_nuget_dll_path()
        if dll_dir:
            if dll_dir not in sys.path:
                sys.path.insert(0, dll_dir)
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(dll_dir)
    except ImportError:
        pass


def _add_reference_safe(assembly_name: str):
    """Add a .NET assembly reference, falling back to full-path search."""
    import clr  # type: ignore[import-untyped]

    try:
        clr.AddReference(assembly_name)
        return
    except Exception:
        pass

    # Try by full path in the NuGet DLL cache
    try:
        from pywinui.sdk_installer import get_nuget_dll_path

        dll_dir = get_nuget_dll_path()
        if dll_dir:
            full_path = os.path.join(dll_dir, assembly_name + ".dll")
            if os.path.isfile(full_path):
                clr.AddReference(full_path)
                return
    except Exception:
        pass

    raise RuntimeError(
        f"Cannot load assembly '{assembly_name}'. Run: pywinui setup"
    )
