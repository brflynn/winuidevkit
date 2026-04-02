# Adding a New Language Pack

This guide walks through creating a WinUIDevKit language pack for a new language.

## Step 1: Identify the Bridge

Before writing any code, determine whether an existing WinRT bridge exists for your language:

| Category | Action |
|----------|--------|
| **First-party Microsoft bridge** (e.g., windows-rs for Rust) | Use it directly |
| **Community bridge** (e.g., pythonnet, swift-winrt) | Use it if actively maintained |
| **COM-only bridge** (e.g., go-ole for Go) | Extend with WinRT projection |
| **No bridge exists** | Create a new one (N-API addon, FFI, or direct vtable calls) |

## Step 2: Create the Language Pack Directory

```
src/<language>/
├── README.md           # Bridge info, prerequisites, architecture
├── <package-config>    # Cargo.toml, package.json, go.mod, etc.
└── src/
    ├── bootstrap.*     # MddBootstrapInitialize2 wrapper
    ├── xaml_loader.*   # XamlReader.Load wrapper
    └── binder.*        # FindName + event wiring
```

## Step 3: Implement the Four Components

### 3a. Bootstrap

Wrap `MddBootstrapInitialize2(0x00010008, null, {0}, 0)`:

```
function initialize():
    result = call MddBootstrapInitialize2(0x00010008, null, MinVersion{0}, 0)
    if result < 0:
        throw error("Bootstrap failed: " + hex(result))

function shutdown():
    call MddBootstrapShutdown()
```

### 3b. XAML Loader

Wrap `XamlReader.Load(string)`:

```
function loadXaml(xamlString):
    // Inject default namespace if missing
    if "schemas.microsoft.com/winfx/2006/xaml/presentation" not in xamlString:
        inject it

    element = XamlReader.Load(xamlString)
    return element
```

### 3c. Binder

Wrap `FrameworkElement.FindName(string)`:

```
function findElement(root, name):
    return root.FindName(name)

function extractNames(xamlString):
    return regex_find_all('x:Name="([^"]+)"', xamlString)

function buildBindings(root, xamlString):
    bindings = {}
    for name in extractNames(xamlString):
        bindings[name] = findElement(root, name)
    return bindings
```

### 3d. Event Wiring (optional but recommended)

```
function wireEvents(bindings, handlerObject):
    for each method in handlerObject:
        if method matches "on_<name>_<event>":
            element = bindings[name]
            element.add_handler(event, method)
```

## Step 4: Create an Example

Add `examples/<language>-helloworld/` with:

- `app/MainWindow.xaml` — Use the shared XAML template
- `app/main.<ext>` — Minimal app that opens a window with a click counter

## Step 5: Add a README

Your language pack's `README.md` should cover:

1. Which bridge is used and why (existing vs. new)
2. Prerequisites (compiler, runtime, SDK version)
3. Quick start instructions
4. Architecture diagram showing your language → bridge → WinUI3 stack

## Step 6: Update the Root README

Add your language to the table in [`README.md`](../README.md):

```markdown
| Language | Bridge | Status |
|----------|--------|--------|
| YourLang | bridge-name | 🚧 In Progress |
```

## Step 7: CI (optional)

Add a GitHub Actions job to `.github/workflows/ci.yml` that builds your language
pack on `windows-latest`.
