"""CLI entry-point for pywinui: init, run, build."""

import os
import shutil
import subprocess
import sys

import click


@click.group()
@click.version_option(package_name="pywinui")
def main():
    """pywinui – Build native WinUI3 desktop apps with Python + XAML."""


@main.command()
@click.argument("name")
def init(name: str):
    """Scaffold a new pywinui project."""
    dest = os.path.join(os.getcwd(), name)
    if os.path.exists(dest):
        click.echo(f"Error: directory '{name}' already exists.", err=True)
        raise SystemExit(1)

    template_dir = os.path.join(os.path.dirname(__file__), "templates", "default")
    if not os.path.isdir(template_dir):
        click.echo("Error: built-in project template not found.", err=True)
        raise SystemExit(1)

    shutil.copytree(template_dir, dest)

    # Personalise placeholders
    _replace_in_file(os.path.join(dest, "pyproject.toml"), "{{PROJECT_NAME}}", name)
    _replace_in_file(os.path.join(dest, "pywinui.toml"), "{{PROJECT_NAME}}", name)
    _replace_in_file(os.path.join(dest, "README.md"), "{{PROJECT_NAME}}", name)
    _replace_in_file(
        os.path.join(dest, "app", "MainWindow.xaml"), "{{PROJECT_NAME}}", name
    )

    click.echo(f"Created project '{name}' at {dest}")
    click.echo(f"  cd {name}")
    click.echo("  pywinui run")


@main.command()
@click.option(
    "--config",
    default="pywinui.toml",
    help="Path to pywinui.toml config file.",
)
def run(config: str):
    """Run the WinUI3 app in development mode."""
    cfg = _load_config(config)
    xaml = cfg.get("app", {}).get("xaml", "app/MainWindow.xaml")
    codebehind = cfg.get("app", {}).get("codebehind", "app.main:MainWindow")

    # Launch via the runtime (cwd = directory containing the config file)
    project_dir = os.path.dirname(os.path.abspath(config))
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pywinui_runtime",
            "--xaml",
            xaml,
            "--codebehind",
            codebehind,
        ],
        cwd=project_dir,
        check=True,
    )


@main.command()
@click.option(
    "--config",
    default="pywinui.toml",
    help="Path to pywinui.toml config file.",
)
def build(config: str):
    """Package the app into a distributable exe + support files."""
    cfg = _load_config(config)
    app_name = cfg.get("project", {}).get("name", "MyApp")
    entry = cfg.get("app", {}).get("entry", "app/main.py")

    click.echo(f"Building '{app_name}' ...")
    from pywinui.packager import package_app

    package_app(app_name=app_name, entry=entry, config=cfg)
    click.echo("Build complete. Output in dist/")


@main.command()
def designer():
    """Open the XAML designer shim in Visual Studio / Blend.

    This opens a lightweight .csproj/.sln that gives you full WinUI3 XAML
    IntelliSense and visual designer support. Edit your XAML visually,
    then return to VS Code for the Python code-behind.
    """
    sln = os.path.join(os.getcwd(), "designer", "XamlDesigner.sln")
    if not os.path.isfile(sln):
        click.echo("Error: designer/XamlDesigner.sln not found.", err=True)
        click.echo("Run 'pywinui init <name>' to create a project with designer support.")
        raise SystemExit(1)

    click.echo("Opening XAML designer in Visual Studio...")
    click.echo("  Edit XAML visually, then save and return to VS Code.")
    os.startfile(sln)


@main.command()
def setup():
    """Install Windows App SDK runtime and dependencies.

    Downloads the WinUI3 runtime installer, the managed NuGet DLLs,
    and pythonnet. Run this once before your first `pywinui run`.
    """
    from pywinui.sdk_installer import install_sdk, is_sdk_installed

    if is_sdk_installed():
        click.echo("Windows App SDK runtime is already installed.")
    else:
        click.echo("Windows App SDK not detected. Installing...")

    try:
        success = install_sdk(verbose=True, interactive=True)
        if success:
            click.echo()
            click.echo("Setup complete! You can now run:")
            click.echo("  pywinui init MyApp")
            click.echo("  cd MyApp")
            click.echo("  pywinui run")
        else:
            click.echo()
            click.echo("Partial setup. The runtime installer may need admin rights.")
            click.echo("Try running this as Administrator:")
            click.echo("  pywinui setup")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@main.command()
def doctor():
    """Check that all pywinui dependencies are correctly installed."""
    click.echo("pywinui doctor")
    click.echo("=" * 40)
    ok = True

    # Python version
    import platform as plat

    click.echo(f"  Python:         {sys.version.split()[0]}")

    # OS
    click.echo(f"  Platform:       {plat.platform()}")
    click.echo(f"  Architecture:   {plat.machine()}")

    # Windows App SDK runtime
    from pywinui.sdk_installer import is_sdk_installed, get_nuget_dll_path

    if is_sdk_installed():
        click.echo("  WinAppSDK:      installed (system)")
    elif get_nuget_dll_path():
        click.echo("  WinAppSDK:      installed (NuGet cache)")
    else:
        click.echo("  WinAppSDK:      NOT FOUND")
        click.echo("                  Run: pywinui setup")
        ok = False

    # pythonnet
    try:
        import clr  # type: ignore[import-untyped]

        click.echo("  pythonnet:      installed")
    except ImportError:
        click.echo("  pythonnet:      NOT FOUND")
        click.echo("                  Run: pip install pythonnet")
        ok = False

    # NuGet DLLs
    dll_path = get_nuget_dll_path()
    if dll_path:
        click.echo(f"  NuGet DLLs:     {dll_path}")
    else:
        click.echo("  NuGet DLLs:     NOT FOUND")
        click.echo("                  Run: pywinui setup")
        ok = False

    click.echo("=" * 40)
    if ok:
        click.echo("All checks passed!")
    else:
        click.echo("Some checks failed. Run: pywinui setup")


# ── helpers ──────────────────────────────────────────────────────────────

def _load_config(path: str) -> dict:
    import toml

    if not os.path.isfile(path):
        click.echo(f"Error: config file '{path}' not found.", err=True)
        raise SystemExit(1)
    return toml.load(path)


def _replace_in_file(filepath: str, old: str, new: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
