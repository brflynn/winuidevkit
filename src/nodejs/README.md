# Node.js Language Pack

**WinUI3 for Node.js via a new N-API native addon.**

## Quick Start

```powershell
# 1. Install (downloads from WinUIDevKit release — no clone needed)
irm https://github.com/brflynn/WinUIDevKit/releases/latest/download/install.ps1 -OutFile install.ps1
.\install.ps1 -Language nodejs

# 2. One-time: install Windows App SDK
winuidev setup

# 3. Create and run a project
winuidev init MyApp
cd MyApp
winuidev run
```

## Why a Custom Addon?

There is no maintained public bridge from Node.js to WinRT/WinUI3.
[NodeRT](https://github.com/nicktechnlogy/nodert) was archived in 2023.
This language pack includes a **new C++ N-API addon** that wraps C++/WinRT
headers and exposes bootstrap, XAML loading, and element lookup to JavaScript.

| Existing option | Status | Problem |
|----------------|--------|---------|
| NodeRT | ❌ Archived (2023) | No WinUI3 support |
| edge-js | ⚠️ Active | .NET bridge, adds CLR overhead |
| node-ffi-napi | ⚠️ Active | Too low-level for WinRT vtables |
| **N-API + C++/WinRT** | ✅ Our approach | Direct, no intermediary runtime |

## Architecture

```
Node.js process
  └─ N-API addon (C++/WinRT)
       ├─ bootstrap.cpp       — MddBootstrapInitialize
       ├─ xaml_loader.cpp     — XamlReader::Load, Window
       ├─ binder.cpp          — FindName, event bridge
       └─ message_pump.cpp    — DispatcherQueue ↔ libuv
  └─ TypeScript
       ├─ cli.ts              — winuidev init/run/build
       ├─ runtime.ts          — JS API over the addon
       └─ binder.ts           — x:Name → JS object mapping
```

## Requirements

- Node.js 18+ (with N-API)
- C++ build tools (Visual Studio Build Tools or MSVC)
- Windows 10/11 (x64)
- Windows App SDK 1.8
