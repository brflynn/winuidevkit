"""Allow running pywinui_runtime as ``python -m pywinui_runtime``."""

import argparse
import sys

from pywinui_runtime.app import App


def main():
    parser = argparse.ArgumentParser(description="pywinui runtime launcher")
    parser.add_argument("--xaml", required=True, help="Path to the XAML file")
    parser.add_argument("--codebehind", default=None, help="module.path:ClassName")
    args = parser.parse_args()

    App.run(xaml=args.xaml, codebehind=args.codebehind)


if __name__ == "__main__":
    main()
