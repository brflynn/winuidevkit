# Swift Language Pack

**WinUI3 for Swift via [swift-winrt](https://github.com/thebrowsercompany/swift-winrt) — no new bridge needed.**

## Quick Start

```bash
swift build                         # 1. Build the CLI
winuidev setup                      # 2. One-time SDK install
winuidev init MyApp                 # 3. Scaffold a project
cd MyApp
winuidev run                        # 4. Launch the app
```

## How It Works

swift-winrt (maintained by The Browser Company, makers of Arc) generates Swift
projections from WinRT metadata, giving idiomatic Swift access to all WinUI3
types. **No new bridge code is needed.** This language pack provides only the
bootstrap/XAML/binder convenience layer.

```
┌─────────────────────────────────────┐
│  Your Swift App                     │
│  ┌────────────────┐ ┌────────────┐  │
│  │ Bootstrap.swift │ │Binder.swift│  │
│  └──────┬─────────┘ └──────┬─────┘  │
│         │                  │        │
│  ┌──────▼──────────────────▼─────┐  │
│  │  swift-winrt projections      │  │ ← existing bridge
│  └──────────────┬────────────────┘  │
│                 │                   │
│  ┌──────────────▼────────────────┐  │
│  │  Windows App SDK / WinUI3     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Requirements

- Swift 5.9+ for Windows
- swift-winrt package
- Windows 10/11 (x64)
- Windows App SDK 1.8
