# WinUIDevKit

**Native WinUI3 desktop apps from any language.**

WinUIDevKit provides language packs that let developers build XAML-first WinUI3 apps
using their preferred programming language — Python, Rust, Go, Node.js, and more.

## Architecture

Every language follows the same pattern:

```
┌─────────────────────────────────────────────────┐
│  Your App Code (Python / Rust / Go / Node.js)   │
├─────────────────────────────────────────────────┤
│  Language Pack                                   │
│  ┌──────────┐ ┌────────┐ ┌──────────┐ ┌──────┐ │
│  │Bootstrap │ │  XAML   │ │  Binder  │ │ CLI  │ │
│  │          │ │ Loader  │ │ (x:Name) │ │      │ │
│  └──────────┘ └────────┘ └──────────┘ └──────┘ │
├─────────────────────────────────────────────────┤
│  Core (shared XAML templates, SDK scripts, CI)   │
├─────────────────────────────────────────────────┤
│  Windows App SDK 1.8  (WinRT / COM)              │
├─────────────────────────────────────────────────┤
│  Windows 10/11                                   │
└─────────────────────────────────────────────────┘
```

Each language pack implements four components:

| Component | What it does |
|-----------|-------------|
| **Bootstrap** | Initialize Windows App Runtime (DDLM), load assemblies/DLLs |
| **XAML Loader** | Parse XAML files, call `XamlReader.Load()` via the language's WinRT/COM bridge |
| **Binder** | Map `x:Name` elements to language-native constructs + wire events |
| **CLI** | `init` / `run` / `build` commands for the developer workflow |

## Language Packs

| Language | Status | Bridge Technology | Package |
|----------|--------|-------------------|---------|
| [Python](src/languagepacks/python/) | ✅ Released | pythonnet (CoreCLR) | `pip install winuidevkit-python` |
| [Rust](src/languagepacks/rust/) | 🚧 In Progress | windows-rs (COM/WinRT) | `cargo add winuidevkit` |
| [Go](src/languagepacks/go/) | 🚧 In Progress | go-ole + go-winrt | `go get winuidevkit` |
| [Node.js](src/languagepacks/nodejs/) | 📋 Planned | node-ffi / N-API | `npm install winuidevkit` |
| [Kotlin](src/languagepacks/kotlin/) | 📋 Planned | Kotlin/Native + COM | Maven |
| [Java](src/languagepacks/java/) | 📋 Planned | JNA + COM | Maven |
| [Swift](src/languagepacks/swift/) | 📋 Planned | C interop + COM | SPM |

## Quick Start (any language)

The workflow is the same regardless of language:

```bash
# 1. Install the language pack
pip install winuidevkit-python          # Python
cargo install winuidevkit-cli           # Rust
go install winuidevkit/cmd/winui@latest # Go
npm install -g winuidevkit              # Node.js

# 2. One-time setup (downloads Windows App SDK)
winui setup

# 3. Scaffold a project
winui init MyApp
cd MyApp

# 4. Run it
winui run

# 5. Package for distribution
winui build
```

## Repo Structure

```
WinUIDevKit/
  src/
    core/                          # Shared across all languages
      sdk/                         # SDK discovery + installer scripts
      xaml-templates/              # Starter XAML files
      manifests/                   # AppxManifest templates
      ci/                          # Reusable CI/CD workflows
    languagepacks/
      python/                      # Python language pack (pywinui)
      rust/                        # Rust language pack
      go/                          # Go language pack
      nodejs/                      # Node.js language pack
      kotlin/                      # Kotlin language pack (planned)
      java/                        # Java language pack (planned)
      swift/                       # Swift language pack (planned)
  examples/
    python-helloworld/
    rust-helloworld/
    go-helloworld/
    nodejs-helloworld/
  docs/
    architecture.md
    adding-a-language.md
    bootstrap-protocol.md
```

## How Languages Talk to WinUI3

The Windows App SDK exposes everything via COM/WinRT interfaces. Each language
reaches those interfaces differently:

| Language | Mechanism | Key Dependency |
|----------|-----------|----------------|
| Python | .NET interop via pythonnet → CsWinRT projections | pythonnet 3.x + CoreCLR |
| Rust | Direct WinRT/COM via `windows` crate | microsoft/windows-rs |
| Go | COM vtable calls via `go-ole` | go-ole/go-ole |
| Node.js | N-API native addon wrapping C++/WinRT | Custom C++ addon |
| Kotlin | Kotlin/Native calling COM via cinterop | Kotlin/Native compiler |
| Java | JNA mapping COM vtables | net.java.dev.jna |
| Swift | C bridging header → COM vtables | Swift on Windows toolchain |

## Contributing

See [docs/adding-a-language.md](docs/adding-a-language.md) for the step-by-step
guide to adding a new language pack.

## License

MIT
