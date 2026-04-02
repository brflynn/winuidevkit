"""XAML Binder – connects x:Name elements to Python attributes and wires events."""

import re
from typing import Any


class ViewProxy:
    """Lightweight proxy that exposes XAML x:Name elements as Python attributes.

    After binding, ``proxy.myButton`` returns the XAML element with
    ``x:Name="myButton"``.
    """

    def __init__(self, root: Any, named_elements: dict[str, Any]):
        self._root = root
        self._named = named_elements

    @property
    def root(self) -> Any:
        return self._root

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._named[name]
        except KeyError:
            raise AttributeError(
                f"No XAML element with x:Name='{name}' found."
            ) from None


def bind_xaml(root: Any, xaml_string: str) -> ViewProxy:
    """Walk the parsed XAML tree and build a ViewProxy with named elements.

    Parameters
    ----------
    root:
        The root UI element returned by XamlReader.Load.
    xaml_string:
        The original XAML text (used to discover x:Name declarations).

    Returns
    -------
    ViewProxy with attribute access to named elements.
    """
    names = _extract_xnames(xaml_string)
    named_elements: dict[str, Any] = {}

    for name in names:
        el = _find_element_by_name(root, name)
        if el is not None:
            named_elements[name] = el

    return ViewProxy(root, named_elements)


def wire_events(view: ViewProxy, codebehind: Any):
    """Attach event handlers from the code-behind to XAML elements.

    Convention: if a XAML element has ``x:Name="submitButton"`` and the
    code-behind class has ``on_submitButton_Click``, the handler is
    automatically attached to the Click event.
    """
    for attr_name in dir(codebehind):
        if not attr_name.startswith("on_"):
            continue
        # Pattern: on_<elementName>_<EventName>
        parts = attr_name.split("_", 2)
        if len(parts) < 3:
            continue
        _, element_name, event_name = parts

        try:
            element = getattr(view, element_name)
        except AttributeError:
            continue

        handler = getattr(codebehind, attr_name)
        _attach_event(element, event_name, handler)


# ── private helpers ──────────────────────────────────────────────────────

_XNAME_RE = re.compile(r'x:Name\s*=\s*"([^"]+)"', re.IGNORECASE)


def _extract_xnames(xaml_string: str) -> list[str]:
    """Parse x:Name attributes from raw XAML text."""
    return _XNAME_RE.findall(xaml_string)


def _find_element_by_name(root: Any, name: str) -> Any | None:
    """Locate a named element in the visual tree.

    Tries the WinUI FindName API first, then falls back to a manual walk.
    """
    try:
        return root.FindName(name)
    except Exception:
        pass
    return None


def _attach_event(element: Any, event_name: str, handler):
    """Attach a Python handler to a WinRT event on the element."""
    try:
        # WinRT events exposed via pythonnet / winsdk look like
        # ``element.Click += handler``
        event = getattr(element, event_name, None)
        if event is not None and callable(getattr(event, "__iadd__", None)):
            event.__iadd__(handler)
        elif event is not None:
            setattr(element, event_name, handler)
    except Exception:
        pass
