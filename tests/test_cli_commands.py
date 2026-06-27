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
Tests for the CLI commands.

This module ensures that the command line interfaces execute properly,
including the `open` command and its interactions with path resolution.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from patkit.cli_commands import open_in_annotator
from patkit.constants import OpenPathType


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


@patch("patkit.cli_commands.resolve_open_path")
@patch("patkit.cli_commands.resolve_scenario_path")
def test_cli_open_manifest(
    mock_resolve_scenario: MagicMock,
    mock_resolve_path: MagicMock,
    runner: CliRunner,
    tmp_path: Path,
) -> None:
    """
    Test that opening a manifest path delegates to the correct scenario.

    Parameters
    ----------
    mock_resolve_scenario : MagicMock
        Mock for resolving scenario path.
    mock_resolve_path : MagicMock
        Mock for resolving the open path.
    runner : CliRunner
        The Click CLI runner.
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    mock_resolve_path.return_value = (
        OpenPathType.MANIFEST,
        Path("dummy_manifest"),
    )
    mock_resolve_scenario.return_value = Path("dummy_scenario")

    with (
        patch(
            "patkit.cli_commands.initialise_config",
            return_value=(MagicMock(), MagicMock()),
        ),
        patch("patkit.cli_commands.initialise_patkit"),
        patch("patkit.cli_commands.run_annotator"),
    ):
        # Use str(tmp_path) so click.Path(exists=True) succeeds
        result = runner.invoke(
            open_in_annotator, args=[str(tmp_path)]
        )

        assert result.exit_code == 0
        mock_resolve_scenario.assert_called_once_with(
            path=Path("dummy_manifest")
        )


@patch("patkit.cli_commands.resolve_open_path")
def test_cli_open_scenario(
    mock_resolve_path: MagicMock,
    runner: CliRunner,
    tmp_path: Path,
) -> None:
    """
    Test that opening a scenario path succeeds.

    Parameters
    ----------
    mock_resolve_path : MagicMock
        Mock for resolving the open path.
    runner : CliRunner
        The Click CLI runner.
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    mock_resolve_path.return_value = (
        OpenPathType.SCENARIO,
        Path("dummy_dir"),
    )

    with (
        patch(
            "patkit.cli_commands.initialise_config",
            return_value=(MagicMock(), MagicMock()),
        ),
        patch("patkit.cli_commands.initialise_patkit"),
        patch("patkit.cli_commands.run_annotator"),
    ):
        result = runner.invoke(open_in_annotator, args=[str(tmp_path)])
        assert result.exit_code == 0


@patch("patkit.cli_commands.resolve_open_path")
@pytest.mark.parametrize(
    "path_type",
    [OpenPathType.DIRECTORY, OpenPathType.SINGLE_DATA],
)
def test_cli_open_unsupported_types_fail(
    mock_resolve_path: MagicMock,
    runner: CliRunner,
    path_type: OpenPathType,
    tmp_path: Path,
) -> None:
    """
    Test that unsupported path types raise a NotImplementedError.

    Parameters
    ----------
    mock_resolve_path : MagicMock
        Mock for resolving the open path.
    runner : CliRunner
        The Click CLI runner.
    path_type : OpenPathType
        The path type to simulate returning from the resolver.
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    mock_resolve_path.return_value = (path_type, Path("dummy_path"))

    with pytest.raises(expected_exception=NotImplementedError):
        runner.invoke(
            open_in_annotator,
            args=[str(tmp_path)],
            catch_exceptions=False,
        )
