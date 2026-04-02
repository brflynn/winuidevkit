# Node.js Language Pack

**WinUI3 for Node.js via a NEW N-API native addon.**

## Bridge: NEW (NodeRT is archived, no maintained alternative)

There is no maintained public bridge from Node.js to WinRT/WinUI3.
[NodeRT](https://github.com/nicktechnlogy/nodert) was archived in 2023.
This language pack includes a **new C++ N-API addon** that:

- Wraps C++/WinRT headers to access WinUI3 types
- Exposes bootstrap, XAML loading, and element lookup to JavaScript
- Runs on the Node.js event loop (WinUI3 message pump bridged via a native thread)

## Architecture

```
Node.js process
  └─ N-API addon (C++/WinRT)
       ├─ bootstrap.cpp     — MddBootstrapInitialize
       ├─ xaml_loader.cpp   — XamlReader::Load, Window, Application
       ├─ binder.cpp        — FindName, event callback bridge
       └─ message_pump.cpp  — Bridge WinUI3 DispatcherQueue ↔ libuv
  └─ JavaScript/TypeScript
       ├─ cli.ts            — winui init/run/build
       ├─ runtime.ts        — JS API over the N-API addon
       └─ binder.ts         — x:Name → JS object mapping
```

## Why a Custom Addon is Needed

| Existing option | Status | Problem |
|----------------|--------|---------|
| NodeRT | ❌ Archived (2023) | No WinUI3 support, no maintenance |
| edge-js | ⚠️ Active | .NET bridge, not direct WinRT. Could work but adds CLR overhead. |
| node-ffi-napi | ⚠️ Active | Too low-level for WinRT vtables, no HSTRING support |
| **N-API + C++/WinRT** | ✅ Our approach | Direct, no intermediary runtime, best performance |

## Key Challenge: Message Pump

WinUI3 requires its own UI thread with a `DispatcherQueue`. Node.js uses libuv.
The addon bridges these:

1. N-API addon spawns a dedicated UI thread running the WinUI3 message pump
2. JS calls marshal to UI thread via `DispatcherQueue.TryEnqueue()`
3. UI events marshal back to Node.js via `napi_threadsafe_function`
