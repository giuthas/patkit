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
Tests for the Qt Annotator GUI components.

This module ensures that the main window behaves correctly when opening
data, dispatching path resolution, and handling unsupported types.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from patkit.constants import OpenPathType
from patkit.qt_annotator import PdQtAnnotator


@pytest.fixture
def mock_annotator() -> MagicMock:
    """
    Provide a mocked PdQtAnnotator instance for testing.

    This avoids the need for a running X server or QApplication.

    Returns
    -------
    MagicMock
        The mocked annotator instance.
    """
    mock_self = MagicMock(spec=PdQtAnnotator)
    mock_self.open = PdQtAnnotator.open.__get__(
        mock_self, PdQtAnnotator
    )

    # Provide the mocked UI elements/instance variables that open()
    # tries to access, which are normally created in __init__
    mock_self.go_to_line_edit = MagicMock()
    mock_self.figure = MagicMock()
    mock_self.mode = MagicMock()

    return mock_self


# Add QIntValidator to the patches to prevent C++ TypeError bindings
@patch("patkit.qt_annotator.QIntValidator")
@patch(
    "patkit.qt_annotator.QFileDialog.getExistingDirectory",
    return_value="/fake/dir",
)
@patch("patkit.qt_annotator.resolve_open_path")
@patch("patkit.qt_annotator.get_manifest_scenarios")
@patch("patkit.qt_annotator.initialise_config")
@patch("patkit.qt_annotator.initialise_patkit")
def test_gui_open_manifest(
    mock_init_patkit: MagicMock,
    mock_init_config: MagicMock,
    mock_get_scenarios: MagicMock,
    mock_resolve_path: MagicMock,
    mock_file_dialog: MagicMock,
    mock_qint_validator: MagicMock,
    mock_annotator: MagicMock,
) -> None:
    """
    Test that opening a manifest via the GUI initializes correctly.

    Parameters
    ----------
    mock_init_patkit : MagicMock
        Mock for initializing patkit session.
    mock_init_config : MagicMock
        Mock for initializing config.
    mock_get_scenarios : MagicMock
        Mock for retrieving scenario paths from manifest.
    mock_resolve_path : MagicMock
        Mock for resolving open path.
    mock_file_dialog : MagicMock
        Mock for the QFileDialog.
    mock_qint_validator : MagicMock
        Mock for PyQt6 QIntValidator.
    mock_annotator : MagicMock
        Mocked annotator fixture.
    """
    mock_resolve_path.return_value = (
        OpenPathType.MANIFEST,
        Path("/fake/dir"),
    )
    mock_get_scenarios.return_value = [Path("/fake/dir/scenario_1")]
    mock_init_config.return_value = (MagicMock(), MagicMock())

    mock_session = MagicMock()
    mock_session.recordings = []
    mock_init_patkit.return_value = mock_session

    mock_annotator.open()

    mock_init_config.assert_called_once_with(
        path=Path("/fake/dir/scenario_1"), require_gui=True
    )
    mock_annotator.update.assert_called_once()
    mock_annotator.update_ui.assert_called_once()


@patch(
    "patkit.qt_annotator.QFileDialog.getExistingDirectory",
    return_value="/fake/dir",
)
@patch("patkit.qt_annotator.resolve_open_path")
@pytest.mark.parametrize(
    "path_type",
    [OpenPathType.DIRECTORY, OpenPathType.SINGLE_DATA],
)
def test_gui_open_unsupported_types_fail(
    mock_resolve_path: MagicMock,
    mock_file_dialog: MagicMock,
    mock_annotator: MagicMock,
    path_type: OpenPathType,
) -> None:
    """
    Test that unsupported path types via the GUI raise errors.

    Parameters
    ----------
    mock_resolve_path : MagicMock
        Mock for resolving open path.
    mock_file_dialog : MagicMock
        Mock for the QFileDialog.
    mock_annotator : MagicMock
        Mocked annotator fixture.
    path_type : OpenPathType
        The path type to simulate returning from the resolver.
    """
    mock_resolve_path.return_value = (path_type, Path("/fake/dir"))

    with pytest.raises(expected_exception=NotImplementedError):
        mock_annotator.open()
