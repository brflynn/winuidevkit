# WinUIDevKit

**Build native WinUI3 desktop apps from any language.**

WinUIDevKit is an open-source toolkit that lets you create Windows desktop applications using WinUI3 and XAML from your preferred programming language. Write your UI in XAML, write your logic in Python, Rust, Go, Node.js, or Swift — WinUIDevKit handles the runtime bridge.

## Install

**One-liner** (interactive — prompts for your language):

```powershell
irm https://github.com/brflynn/WinUIDevKit/releases/latest/download/install.ps1 | iex
```

Or specify the language directly:

```powershell
irm https://github.com/brflynn/WinUIDevKit/releases/latest/download/install.ps1 -OutFile install.ps1
.\install.ps1 -Language python
```

Or download a language pack zip manually from the [latest release](https://github.com/brflynn/WinUIDevKit/releases/latest).

## Get Started

Every language follows the same workflow after install:

```bash
winuidev setup       # one-time: install Windows App SDK
winuidev init MyApp  # scaffold a new project
cd MyApp
winuidev run         # launch the app
winuidev build       # package for distribution
```

## Supported Languages

| Language | Bridge | Status | Guide |
|----------|--------|--------|-------|
| **[Python](src/python/README.md)** | [pythonnet](https://github.com/pythonnet/pythonnet) (existing) | ✅ Released | [Quick Start](src/python/README.md) |
| **[Rust](src/rust/README.md)** | [windows-rs](https://github.com/microsoft/windows-rs) (existing) | 🚧 In Progress | [Quick Start](src/rust/README.md) |
| **[Go](src/go/README.md)** | [go-ole](https://github.com/go-ole/go-ole) + new WinRT projection | 🚧 In Progress | [Quick Start](src/go/README.md) |
| **[Node.js](src/nodejs/README.md)** | New N-API C++/WinRT addon | 🚧 In Progress | [Quick Start](src/nodejs/README.md) |
| **[Swift](src/swift/README.md)** | [swift-winrt](https://github.com/thebrowsercompany/swift-winrt) (existing) | 🚧 In Progress | [Quick Start](src/swift/README.md) |

Each release includes a zip per language containing the CLI, runtime, and SDK installer. No repo clone or package manager needed.

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
