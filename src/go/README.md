# Go Language Pack

**WinUI3 for Go via [go-ole](https://github.com/go-ole/go-ole) + a new WinRT projection.**

## Quick Start

```bash
go install github.com/user/winuidevkit-go/cmd/winuidev@latest  # 1. Install CLI
winuidev setup                                                  # 2. One-time SDK install
winuidev init MyApp                                             # 3. Scaffold a project
cd MyApp
winuidev run                                                    # 4. Launch the app
```

## Why a Custom WinRT Projection?

go-ole provides COM `IUnknown`/`IDispatch` support, but WinUI3 uses WinRT
(`IInspectable`) interfaces. This language pack includes a **new minimal WinRT
projection** in `winrt/`:

| Layer | go-ole covers? | This pack |
|-------|---------------|-----------|
| COM IUnknown | ✅ Yes | Use as-is |
| WinRT IInspectable | ❌ No | **New** — `winrt/winrt.go` |
| WinRT Activation | ❌ No | **New** — `RoActivateInstance` |
| HSTRING | ❌ No | **New** — create/delete/string |

The projection is intentionally minimal — only the WinUI3 types needed for
XAML apps.

## Requirements

- Go 1.21+
- Windows 10/11 (x64)
- Windows App SDK 1.8
