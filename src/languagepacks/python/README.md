# Python Language Pack

**WinUI3 for Python via [pythonnet](https://github.com/pythonnet/pythonnet) (existing public bridge).**

## Bridge: pythonnet (3rd-party, mature)

No new bridge required. pythonnet loads .NET CoreCLR in-process and provides
full access to CsWinRT projections. This language pack only adds:

- **Bootstrap**: Calls `load('coreclr')`, loads assemblies in correct order, initializes DDLM
- **XAML Loader**: Reads `.xaml` files and calls `XamlReader.Load()`
- **Binder**: Maps `x:Name` elements to Python attributes via `FindName()`
- **Event Wiring**: Convention-based `on_<element>_<Event>` pattern
- **CLI**: `winui init/run/build` commands
