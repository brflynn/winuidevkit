# Rust Language Pack

**WinUI3 for Rust via [windows-rs](https://github.com/microsoft/windows-rs) (existing Microsoft bridge).**

## Bridge: windows-rs (1st-party Microsoft, mature)

No new bridge required. The `windows` crate provides direct WinRT/COM bindings
generated from Windows metadata. This language pack only adds:

- **Bootstrap**: DDLM initialization via `MddBootstrapInitialize`
- **XAML Loader**: Safe wrapper around `XamlReader::Load()`
- **Binder**: Maps `x:Name` elements to Rust struct fields via `FindName()`
- **Event Wiring**: Trait-based event handler registration
- **CLI**: `winui init/run/build` (Rust binary)

## How It Works

```
Rust process
  └─ windows crate (direct COM/WinRT vtable calls)
       └─ Microsoft.UI.Xaml (WinUI3 via WinRT activation)
       └─ MddBootstrapInitialize() → DDLM → WinAppSDK native DLLs
```

The `windows` crate generates Rust bindings directly from `.winmd` metadata files.
No .NET runtime is needed — Rust calls WinRT interfaces via COM vtables.

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
