# Go Language Pack

**WinUI3 for Go via [go-ole](https://github.com/go-ole/go-ole) + a new WinRT projection.**

## Quick Start

```powershell
# 1. Install (downloads from WinUIDevKit release — no clone needed)
irm https://github.com/brflynn/WinUIDevKit/releases/latest/download/install.ps1 -OutFile install.ps1
.\install.ps1 -Language go

# 2. One-time: install Windows App SDK
winuidev setup

# 3. Create and run a project
winuidev init MyApp
cd MyApp
winuidev run
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
