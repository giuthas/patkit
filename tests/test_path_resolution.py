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
Tests for path resolution logic.

This module checks whether file and directory paths are accurately
resolved to their corresponding Patkit OpenPathType.
"""
from pathlib import Path

import pytest

from patkit.constants import OpenPathType, PatkitConfigFile, SourceSuffix
from patkit.path_resolution import resolve_open_path


def test_resolve_open_path_manifest(tmp_path: Path) -> None:
    """
    Test resolving a path to a manifest file or directory containing it.

    Parameters
    ----------
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    # Test directory containing a manifest
    manifest_file = tmp_path / PatkitConfigFile.MANIFEST
    manifest_file.touch()

    # When passing the directory
    path_type, target = resolve_open_path(path=tmp_path)
    assert path_type == OpenPathType.MANIFEST
    assert target == manifest_file

    # When passing the manifest file directly
    path_type, target = resolve_open_path(path=manifest_file)
    assert path_type == OpenPathType.MANIFEST
    assert target == manifest_file


def test_resolve_open_path_scenario(tmp_path: Path) -> None:
    """
    Test resolving a path to a scenario configuration file or directory.

    Parameters
    ----------
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    # Test directory containing a data config (making it a scenario)
    config_file = tmp_path / PatkitConfigFile.DATA
    config_file.touch()

    # When passing the directory
    path_type, target = resolve_open_path(path=tmp_path)
    assert path_type == OpenPathType.SCENARIO
    assert target == tmp_path

    # When passing the config file directly
    path_type, target = resolve_open_path(path=config_file)
    assert path_type == OpenPathType.SCENARIO
    # It should correctly resolve back to the parent directory
    assert target == tmp_path


def test_resolve_open_path_single_data(tmp_path: Path) -> None:
    """
    Test resolving a path to a single data file.

    Parameters
    ----------
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    # Test a single data file
    data_file = tmp_path / f"test_recording{SourceSuffix.WAV}"
    data_file.touch()

    path_type, target = resolve_open_path(path=data_file)
    assert path_type == OpenPathType.SINGLE_DATA
    assert target == data_file


def test_resolve_open_path_directory(tmp_path: Path) -> None:
    """
    Test resolving a path to an empty directory.

    Parameters
    ----------
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    # Test an empty directory (no config or manifest)
    path_type, target = resolve_open_path(path=tmp_path)
    assert path_type == OpenPathType.DIRECTORY
    assert target == tmp_path


def test_resolve_open_path_invalid_file(tmp_path: Path) -> None:
    """
    Test that an invalid file extension raises a ValueError.

    Parameters
    ----------
    tmp_path : Path
        Pytest fixture providing a temporary directory.
    """
    # .txt is a valid AAA_PROMPT, so we must use an unknown extension
    # like .xyz
    bad_file = tmp_path / "random_file.xyz"
    bad_file.touch()

    with pytest.raises(
        expected_exception=ValueError,
        match="not a recognized PATKIT configuration",
    ):
        resolve_open_path(path=bad_file)
