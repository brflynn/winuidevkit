# Swift Language Pack

**WinUI3 for Swift via [swift-winrt](https://github.com/thebrowsercompany/swift-winrt) — no new bridge needed.**

## Quick Start

```powershell
# 1. Install (downloads from WinUIDevKit release — no clone needed)
irm https://github.com/brflynn/WinUIDevKit/releases/latest/download/install.ps1 -OutFile install.ps1
.\install.ps1 -Language swift

# 2. One-time: install Windows App SDK
winuidev setup

# 3. Create and run a project
winuidev init MyApp
cd MyApp
winuidev run
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
