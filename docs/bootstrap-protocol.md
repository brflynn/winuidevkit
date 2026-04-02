# Bootstrap Protocol

The bootstrap sequence initializes the Windows App SDK so that WinUI3 APIs
become available to the calling process. Every language pack must implement
this protocol identically.

## Sequence

```
1. Initialize WinRT runtime
   ├── Python: clr_loader.get_coreclr() + pythonnet load('coreclr')
   ├── Rust:   (automatic via windows-rs)
   ├── Go:     RoInitialize(RO_INIT_MULTITHREADED)
   ├── Node.js: winrt::init_apartment() in C++
   └── Swift:  (automatic via swift-winrt)

2. Call MddBootstrapInitialize2
   ├── majorMinorVersion = 0x00010008  (SDK 1.8)
   ├── versionTag = null
   └── minVersion = PACKAGE_VERSION{0}

3. Verify HRESULT >= 0
   └── If negative → throw/return error with hex HRESULT

4. [App runs, uses WinUI3 APIs]

5. Call MddBootstrapShutdown
   └── Releases dynamic dependencies
```

## DLL Resolution

`MddBootstrapInitialize2` is exported from
`Microsoft.WindowsAppRuntime.Bootstrap.dll`. This DLL must be loadable:

- **Packaged apps**: Resolved via the MSIX package graph automatically.
- **Unpackaged apps (DDLM)**: The SDK installer registers the DLL via MSIX
  Dynamic Dependencies. The bootstrap call locates it through the Windows
  package manager.

## SDK Version Encoding

The `majorMinorVersion` parameter packs major and minor into a single `UInt32`:

```
version = (major << 16) | minor
```

| SDK Version | Encoded Value |
|-------------|---------------|
| 1.0 | `0x00010000` |
| 1.5 | `0x00010005` |
| 1.8 | `0x00010008` |

## Assembly Load Chain (Python/.NET specific)

When using pythonnet with CoreCLR, assemblies must be loaded in dependency order:

```
1. Microsoft.WindowsAppRuntime.Bootstrap.Net.dll
2. WinRT.Runtime.dll  (CsWinRT interop layer)
3. Microsoft.Windows.SDK.NET.dll
4. Microsoft.InteractiveExperiences.Projection.dll
5. Microsoft.WinUI.dll
```

Loading out of order causes `FileNotFoundException` for dependent assemblies.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `0x80040154` | COM class not registered | Install WinAppSDK MSIX packages |
| `0x80070002` | DLL not found | Run `Install-WinAppSdk.ps1` to populate cache |
| `0x80073D19` | Package dependency conflict | Uninstall older SDK versions |
| Bootstrap returns 0 but WinUI fails | Missing assembly in chain | Check load order above |
