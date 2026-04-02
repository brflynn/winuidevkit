# Swift Language Pack

## Bridge: swift-winrt (The Browser Company)

Swift has first-class WinRT support via [swift-winrt](https://github.com/thebrowsercompany/swift-winrt),
maintained by The Browser Company (makers of Arc). This generates Swift projections from WinRT metadata,
giving idiomatic Swift access to all WinUI3 types.

**No new bridge code is needed.** This language pack provides only the bootstrap/XAML/binder
convenience layer on top of swift-winrt.

## Prerequisites

- Swift 5.9+ for Windows (swift.org toolchain or Swift Package Manager)
- swift-winrt package (generates WinUI3 bindings from .winmd files)
- Windows App SDK 1.8 installed

## Architecture

```
┌─────────────────────────────────────┐
│  Your Swift App                     │
│  ┌──────────────┐ ┌──────────────┐  │
│  │ bootstrap.swift│ │ binder.swift │  │
│  └──────┬───────┘ └──────┬───────┘  │
│         │                │          │
│  ┌──────▼────────────────▼───────┐  │
│  │  swift-winrt projections      │  │ ← existing bridge
│  │  (WinUI, WinAppSDK, WinRT)   │  │
│  └──────────────┬────────────────┘  │
│                 │                   │
│  ┌──────────────▼────────────────┐  │
│  │  Windows App SDK / WinUI3     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Key Types from swift-winrt

- `Microsoft.UI.Xaml.Window`
- `Microsoft.UI.Xaml.Markup.XamlReader`
- `Microsoft.UI.Xaml.Application`
- `Microsoft.UI.Xaml.Controls.*`
- `Microsoft.Windows.ApplicationModel.DynamicDependency.Bootstrap`
