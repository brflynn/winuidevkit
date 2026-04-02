# Go Language Pack

**WinUI3 for Go via [go-ole](https://github.com/go-ole/go-ole) + custom WinRT projection.**

## Bridge: go-ole (3rd-party, mature) + NEW WinRT projection

`go-ole` provides low-level COM/IUnknown/IDispatch support. However, WinUI3
uses WinRT (IInspectable) interfaces which go-ole does not cover. This language
pack includes:

- **winrt/** — NEW: Minimal WinRT projection for WinUI3 types
  - IInspectable vtable support
  - RoActivateInstance / RoGetActivationFactory wrappers
  - HSTRING helpers
  - WinUI3 type wrappers (Application, Window, XamlReader, etc.)
- **bootstrap.go** — DDLM initialization via MddBootstrapInitialize
- **xaml.go** — XAML file loader via XamlReader::Load
- **binder.go** — x:Name element lookup via FindName
- **CLI** — `winui init/run/build` (Go binary)

## Why a Custom Projection is Needed

| Layer | go-ole covers? | Status |
|-------|---------------|--------|
| COM IUnknown | ✅ Yes | Use as-is |
| COM IDispatch | ✅ Yes | Not needed (WinUI uses WinRT) |
| WinRT IInspectable | ❌ No | **New code in winrt/** |
| WinRT Activation | ❌ No | **New code in winrt/** |
| HSTRING | ❌ No | **New code in winrt/** |

The projection is intentionally minimal — only the WinUI3 types needed for
XAML apps, not a full Windows SDK binding.
