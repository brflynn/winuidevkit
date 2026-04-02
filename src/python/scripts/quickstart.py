#!/usr/bin/env python
"""Quick-start script: build & deploy a pywinui app in one command.

Usage:
    python scripts/quickstart.py                    # from project root
    python scripts/quickstart.py samples/HelloWorld # specify project dir
"""

import os
import subprocess
import sys


def main():
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(project_dir)

    steps = [
        ("Installing pywinui + packaging deps", [sys.executable, "-m", "pip", "install", "pywinui", "pyinstaller", "-q"]),
        ("Building app", ["pywinui", "build"]),
    ]

    for label, cmd in steps:
        print(f"\n>>> {label}...")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"FAILED: {label}", file=sys.stderr)
            raise SystemExit(1)

    print("\n=== Build complete! ===")
    print("Output in dist/ — copy the folder to any Windows machine to run.")


if __name__ == "__main__":
    main()
