#
# Copyright (c) 2019-2026
# Pertti Palo, Scott Moisik, Matthew Faytak, and Motoki Saito.
#
# This file is part of the Phonetic Analysis ToolKIT
# (see https://github.com/giuthas/patkit/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The example data packaged with this program is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License. You should have received a
# copy of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License along with the data. If not,
# see <https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.
#
# When using the toolkit for scientific publications, please cite the
# articles listed in README.md. They can also be found in
# citations.bib in BibTeX format.
#
"""
Integration tests for the PATKIT CLI.

These tests automate the CLI invocations previously found in
`integration_tests.sh`. The GUI and interactive interpreters
are mocked out to prevent the automated test suite from hanging.
"""
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from patkit.cli import run_cli


@pytest.fixture
def runner() -> CliRunner:
    """
    Provide a Click CLI runner for testing commands.

    Returns
    -------
    CliRunner
        The test runner.
    """
    return CliRunner()


def test_cli_bare(runner: CliRunner) -> None:
    """
    Test running patkit with no arguments.

    Parameters
    ----------
    runner : CliRunner
        The Click CLI runner.
    """
    result = runner.invoke(run_cli, catch_exceptions=False)
    # Depending on how your root command is configured, it may exit 0
    # and print help, or exit 2 due to missing arguments.
    assert result.exit_code in (0, 2)


def test_cli_help(runner: CliRunner) -> None:
    """
    Test running patkit with the --help flag.

    Parameters
    ----------
    runner : CliRunner
        The Click CLI runner.
    """
    result = runner.invoke(run_cli, args=["--help"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Usage:" in result.output


@patch("patkit.cli_commands.run_annotator")
def test_cli_default_minimal(
    mock_annotator: MagicMock, runner: CliRunner
) -> None:
    """
    Test running patkit against the minimal scenario implicitly.

    Parameters
    ----------
    mock_annotator : MagicMock
        Mock to prevent GUI blocking.
    runner : CliRunner
        The Click CLI runner.
    """
    result = runner.invoke(
        run_cli, args=["scenarios/minimal"], catch_exceptions=False
    )
    assert result.exit_code == 0
    mock_annotator.assert_called_once()


@patch("patkit.cli_commands.run_annotator")
def test_cli_open_minimal(
    mock_annotator: MagicMock, runner: CliRunner
) -> None:
    """
    Test running the patkit open command on the minimal scenario.

    Parameters
    ----------
    mock_annotator : MagicMock
        Mock to prevent GUI blocking.
    runner : CliRunner
        The Click CLI runner.
    """
    result = runner.invoke(
        run_cli, args=["open", "scenarios/minimal/"], catch_exceptions=False
    )
    assert result.exit_code == 0
    mock_annotator.assert_called_once()


@patch("patkit.cli_commands.run_annotator")
def test_cli_default_tongue_data(
    mock_annotator: MagicMock, runner: CliRunner
) -> None:
    """
    Test running patkit against tongue_data_1_1 implicitly.

    Parameters
    ----------
    mock_annotator : MagicMock
        Mock to prevent GUI blocking.
    runner : CliRunner
        The Click CLI runner.
    """
    result = runner.invoke(
        run_cli,
        args=["scenarios/tongue_data_1_1/"],
        catch_exceptions=False
    )
    assert result.exit_code == 0
    mock_annotator.assert_called_once()


@patch("patkit.cli_commands.run_interpreter")
def test_cli_interact_minimal(
    mock_interpreter: MagicMock, runner: CliRunner
) -> None:
    """
    Test running the interact command on the minimal scenario.

    Parameters
    ----------
    mock_interpreter : MagicMock
        Mock to prevent REPL blocking.
    runner : CliRunner
        The Click CLI runner.
    """
    result = runner.invoke(
        run_cli,
        args=["interact", "scenarios/minimal/"],
        catch_exceptions=False
    )
    assert result.exit_code == 0
    mock_interpreter.assert_called_once()
