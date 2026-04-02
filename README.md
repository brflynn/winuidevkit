# WinUIDevKit

**Build native WinUI3 desktop apps from any language.**

WinUIDevKit is an open-source toolkit that lets you create Windows desktop applications using WinUI3 and XAML from your preferred programming language. Write your UI in XAML, write your logic in Python, Rust, Go, Node.js, or Swift — WinUIDevKit handles the runtime bridge.

## How It Works

Every language follows the same developer workflow:

```bash
winuidev setup       # one-time: install Windows App SDK
winuidev init MyApp  # scaffold a new project
cd MyApp
winuidev run         # launch the app
winuidev build       # package for distribution
```

Under the hood, each language pack implements the same four components — Bootstrap, XAML Loader, Binder, and CLI — using the best available bridge for that language. Where an existing public bridge exists (pythonnet, windows-rs, swift-winrt), we use it. Where none exists (Go WinRT, Node.js WinRT), WinUIDevKit provides a new minimal bridge.

## Supported Languages

| Language | Bridge | Status | Quick Start |
|----------|--------|--------|-------------|
| **[Python](src/python/README.md)** | [pythonnet](https://github.com/pythonnet/pythonnet) (existing) | ✅ Released | `pip install pywinui` |
| **[Rust](src/rust/README.md)** | [windows-rs](https://github.com/microsoft/windows-rs) (existing) | 🚧 In Progress | `cargo add winuidevkit` |
| **[Go](src/go/README.md)** | [go-ole](https://github.com/go-ole/go-ole) + new WinRT projection | 🚧 In Progress | `go get winuidevkit` |
| **[Node.js](src/nodejs/README.md)** | New N-API C++/WinRT addon | 🚧 In Progress | `npm install winuidevkit` |
| **[Swift](src/swift/README.md)** | [swift-winrt](https://github.com/thebrowsercompany/swift-winrt) (existing) | 🚧 In Progress | `swift package add winuidevkit` |

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Your App Code (Python / Rust / Go / Node / Swift)│
├─────────────────────────────────────────────────┤
│  Language Pack                                   │
│  ┌──────────┐ ┌────────┐ ┌──────────┐ ┌──────┐ │
│  │Bootstrap │ │  XAML   │ │  Binder  │ │ CLI  │ │
│  │          │ │ Loader  │ │ (x:Name) │ │      │ │
│  └──────────┘ └────────┘ └──────────┘ └──────┘ │
├─────────────────────────────────────────────────┤
│  Bridge (pythonnet / windows-rs / N-API / etc.)  │
├─────────────────────────────────────────────────┤
│  Windows App SDK 1.8  ·  WinUI3  ·  WinRT/COM   │
└─────────────────────────────────────────────────┘
```

## Repo Structure

```
WinUIDevKit/
  src/
    core/           # Shared SDK installer, XAML templates, MSIX manifests
    python/         # Python language pack (fully working)
    rust/           # Rust language pack (windows-rs)
    go/             # Go language pack (go-ole + WinRT projection)
    nodejs/         # Node.js language pack (N-API addon)
    swift/          # Swift language pack (swift-winrt)
  examples/         # HelloWorld per language
  docs/             # Architecture, bootstrap protocol, contributor guide
```

## Documentation

- [Architecture](docs/architecture.md) — the four-component pattern and bridge layer
- [Bootstrap Protocol](docs/bootstrap-protocol.md) — how WinAppSDK initialization works
- [Adding a Language](docs/adding-a-language.md) — guide for contributing a new language pack

## License

MIT
