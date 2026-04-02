# Architecture

WinUIDevKit follows a **four-component pattern** that is identical across all languages.
Only the bridge layer varies — everything above it is pure language code.

## The Four Components

```
┌──────────────────────────────────────────────┐
│  Your App (any language)                     │
│                                              │
│  1. Bootstrap      — init WinAppSDK DDLM    │
│  2. XAML Loader    — parse XAML → UI tree    │
│  3. Binder         — map x:Name → objects    │
│  4. Event Wiring   — connect handlers        │
│                                              │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│  Bridge Layer (language-specific)            │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│  Windows App SDK / WinUI3                    │
└──────────────────────────────────────────────┘
```

### 1. Bootstrap

Every language pack must call `MddBootstrapInitialize2` (the Dynamic Dependency
Lifetime Manager entry point) before using any WinUI3 API. This function is
exported from `Microsoft.WindowsAppRuntime.Bootstrap.dll`.

| Parameter | Value | Notes |
|-----------|-------|-------|
| majorMinorVersion | `0x00010008` | SDK 1.8 encoded as `(major << 16) \| minor` |
| versionTag | `null` | Release channel |
| minVersion | `0` | No minimum patch requirement |

### 2. XAML Loader

`XamlReader.Load(string)` parses a XAML string and returns a `UIElement` tree.
The XAML must include the WinUI3 default namespace:

```
xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
```

Each language pack's loader injects this automatically if missing.

### 3. Binder

`FrameworkElement.FindName(string)` locates elements by their `x:Name` attribute.
The binder extracts all `x:Name` values from the XAML (via simple regex), then
calls `FindName` on the root to build a name → element dictionary.

### 4. Event Wiring

Events follow the handler naming convention: `on_<x:Name>_<EventName>`.
The binder scans the user's code for matching function names and subscribes
them to the corresponding WinUI3 events.

## Bridge Technology Per Language

| Language | Bridge | Who Maintains | New Code Needed? |
|----------|--------|---------------|------------------|
| Python | pythonnet | pythonnet community | No — existing |
| Rust | windows-rs | Microsoft | No — existing |
| Go | go-ole + custom WinRT | WinUIDevKit | **Yes** — WinRT projection |
| Node.js | N-API C++/WinRT addon | WinUIDevKit | **Yes** — full N-API addon |
| Swift | swift-winrt | The Browser Company | No — existing |

## Shared Core

The `src/core/` directory contains language-agnostic resources:

- **`sdk/Install-WinAppSdk.ps1`** — PowerShell script to detect, download, and cache WinAppSDK
- **`xaml-templates/`** — Starter XAML files with `{{placeholder}}` tokens
- **`manifests/`** — AppxManifest templates for MSIX packaging

These are consumed by each language pack's CLI tooling during `init` and `build` commands.

## Directory Structure

```
WinUIDevKit/
├── src/
│   ├── core/                    # Shared SDK installer, templates, manifests
│   └── languagepacks/
│       ├── python/              # pythonnet bridge (references pywinui)
│       ├── rust/                # windows-rs bridge
│       ├── go/                  # go-ole + NEW WinRT projection
│       ├── nodejs/              # NEW N-API C++/WinRT addon
│       └── swift/               # swift-winrt bridge
├── examples/
│   ├── python-helloworld/
│   ├── rust-helloworld/
│   ├── go-helloworld/
│   ├── nodejs-helloworld/
│   └── swift-helloworld/
└── docs/
```
