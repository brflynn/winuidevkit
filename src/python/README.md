# Python Language Pack

**WinUI3 for Python via [pythonnet](https://github.com/pythonnet/pythonnet) — no new bridge needed.**

## Quick Start

```powershell
# 1. Install (downloads from WinUIDevKit release — no clone needed)
irm https://github.com/brflynn/WinUIDevKit/releases/latest/download/install.ps1 -OutFile install.ps1
.\install.ps1 -Language python

# 2. One-time: install Windows App SDK
winuidev setup

# 3. Create and run a project
winuidev init MyApp
cd MyApp
winuidev run
```

That's it — no repo clone, no PyPI. Five commands from zero to a running WinUI3 window.

## Features

- **XAML-first**: Define your UI with standard WinUI3 XAML
- **Python code-behind**: Access named XAML elements as Python attributes
- **Auto event wiring**: Convention-based `on_<element>_<Event>` handler binding
- **CLI workflow**: `winuidev init` / `run` / `build`
- **Packaging**: `winuidev build` produces a distributable exe + support files

## CLI commands

| Command | Description |
|---------|-------------|
| `winuidev setup` | Install Windows App SDK runtime and NuGet DLLs |
| `winuidev doctor` | Check that all dependencies are installed |
| `winuidev init <name>` | Scaffold a new project with XAML + code-behind |
| `winuidev run` | Run the app in development mode |
| `winuidev build` | Package the app into a distributable exe |

## Project layout

```
MyApp/
  app/
    main.py              # Python code-behind
    MainWindow.xaml      # WinUI3 XAML UI definition
    assets/
  pywinui.toml           # pywinui configuration
  pyproject.toml
```

## Code-behind example

```python
from pywinui_runtime import window

@window("app/MainWindow.xaml")
class MainWindow:
    def __init__(self, view):
        self.view = view
        # view.helloButton → the Button with x:Name="helloButton"

    def on_helloButton_Click(self, sender, args):
        sender.Content = "Clicked!"

if __name__ == "__main__":
    MainWindow.run()
```

## Requirements

- Python 3.10+
- Windows 10 1809+ (x64)
- Windows App SDK Runtime 1.8+ (auto-installed via `winuidev setup`)

## Development

```bash
git clone https://github.com/brflynn/pywinui.git
cd pywinui
pip install -e ".[dev]"
pytest
```

## License

MIT
