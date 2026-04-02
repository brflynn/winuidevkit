# Rust Language Pack

**WinUI3 for Rust via [windows-rs](https://github.com/microsoft/windows-rs) — no new bridge needed.**

## Quick Start

```bash
cargo install winuidevkit-cli       # 1. Install CLI
winuidev setup                      # 2. One-time SDK install
winuidev init MyApp                 # 3. Scaffold a project
cd MyApp
winuidev run                        # 4. Launch the app
```

## How It Works

The `windows` crate (Microsoft 1st-party) generates Rust bindings directly from
`.winmd` metadata files — no .NET runtime needed. Rust calls WinRT interfaces
via COM vtables.

This language pack adds:

- **Bootstrap** — DDLM initialization via `MddBootstrapInitialize`
- **XAML Loader** — safe wrapper around `XamlReader::Load()`
- **Binder** — `FindName()` + `winui_view!` macro for struct field mapping
- **CLI** — `winuidev init / run / build`

## Cargo Features

```toml
[dependencies]
windows = { version = "0.58", features = [
    "Microsoft_UI_Xaml",
    "Microsoft_UI_Xaml_Controls",
    "Microsoft_UI_Xaml_Markup",
    "Microsoft_UI_Xaml_Input",
    "Microsoft_Windows_ApplicationModel_DynamicDependency",
]}
```

## Requirements

- Rust 1.70+ (stable)
- Windows 10/11 (x64)
- Windows App SDK 1.8
