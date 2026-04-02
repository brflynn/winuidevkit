"""Packaging backend – produces an exe + support files via PyInstaller."""

import os
import shutil
import subprocess
import sys


def package_app(app_name: str, entry: str, config: dict):
    """Build a distributable package for the pywinui app.

    Uses PyInstaller to bundle the Python runtime, the app code,
    XAML files, assets, and Windows App SDK DLLs into a single
    directory distribution.
    """
    dist_dir = os.path.join(os.getcwd(), "dist")
    build_dir = os.path.join(os.getcwd(), "build")

    # Collect extra data (XAML + assets)
    add_data: list[str] = []
    app_dir = os.path.dirname(entry) or "app"
    if os.path.isdir(app_dir):
        add_data.append(f"{app_dir}{os.pathsep}{app_dir}")

    # Include Windows App SDK DLLs from the NuGet cache
    dll_dir = _get_sdk_dll_dir()
    if dll_dir:
        add_data.append(f"{dll_dir}{os.pathsep}sdk")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--name",
        app_name,
        "--distpath",
        dist_dir,
        "--workpath",
        build_dir,
    ]
    for ad in add_data:
        cmd.extend(["--add-data", ad])

    # Include pywinui_runtime as hidden import
    cmd.extend(["--hidden-import", "pywinui_runtime"])
    cmd.extend(["--hidden-import", "pywinui_runtime.bootstrap"])
    cmd.extend(["--hidden-import", "pywinui_runtime.app"])
    cmd.extend(["--hidden-import", "pywinui_runtime.binder"])
    cmd.extend(["--hidden-import", "pywinui"])
    cmd.extend(["--hidden-import", "pywinui.sdk_installer"])
    cmd.append(entry)

    subprocess.run(cmd, check=True)

    # Copy any loose support files into the dist folder
    output_dir = os.path.join(dist_dir, app_name)
    _copy_support_files(output_dir)

    # Copy runtimeconfig.json for .NET 8 CoreCLR
    _copy_runtimeconfig(output_dir)

    print(f"\nBuild complete: {output_dir}")
    print(f"Run with: .\\dist\\{app_name}\\{app_name}.exe")


def _get_sdk_dll_dir() -> str | None:
    """Find the pywinui SDK DLL cache directory."""
    try:
        from pywinui.sdk_installer import get_nuget_dll_path
        return get_nuget_dll_path()
    except ImportError:
        return None


def _copy_runtimeconfig(output_dir: str):
    """Copy or create runtimeconfig.json in the output directory."""
    rc_dest = os.path.join(output_dir, "pywinui.runtimeconfig.json")
    if os.path.exists(rc_dest):
        return

    # Check if one exists in the SDK cache
    dll_dir = _get_sdk_dll_dir()
    if dll_dir:
        rc_src = os.path.join(dll_dir, "pywinui.runtimeconfig.json")
        if os.path.isfile(rc_src):
            shutil.copy2(rc_src, rc_dest)
            return

    # Create a minimal one
    import json
    config = {
        "runtimeOptions": {
            "tfm": "net8.0",
            "frameworks": [
                {
                    "name": "Microsoft.WindowsDesktop.App",
                    "version": "8.0.0"
                }
            ]
        }
    }
    with open(rc_dest, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def _copy_support_files(output_dir: str):
    """Copy Windows App Runtime support DLLs if present."""
    support = os.path.join(os.getcwd(), "support")
    if os.path.isdir(support):
        for item in os.listdir(support):
            src = os.path.join(support, item)
            dst = os.path.join(output_dir, item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
