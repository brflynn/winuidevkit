"""Tests for the CLI."""

import os
import tempfile
from unittest.mock import patch

from click.testing import CliRunner

from pywinui.cli import main


def test_init_creates_project():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["init", "TestApp"])
        assert result.exit_code == 0
        assert os.path.isdir("TestApp")
        assert os.path.isfile("TestApp/pywinui.toml")
        assert os.path.isfile("TestApp/app/MainWindow.xaml")
        assert os.path.isfile("TestApp/app/main.py")

        # Check placeholders were replaced
        with open("TestApp/pywinui.toml") as f:
            content = f.read()
        assert "TestApp" in content
        assert "{{PROJECT_NAME}}" not in content


def test_init_existing_dir_fails():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs("Existing")
        result = runner.invoke(main, ["init", "Existing"])
        assert result.exit_code != 0
