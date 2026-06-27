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
"""Unit and integration tests for the PdQtAnnotator window interface."""

from unittest.mock import MagicMock

from patkit.constants import AnnotatorMode
from patkit.qt_annotator import PdQtAnnotator


def test_annotator_initialization(annotator: PdQtAnnotator) -> None:
    """
    Verify that the annotator initializes with correct properties.

    Parameters
    ----------
    annotator : PdQtAnnotator
        The initialized annotator window fixture.
    """
    assert annotator.index == 0
    assert annotator.annotator_mode == AnnotatorMode.ANALYSE
    assert annotator.display_tongue is False


def test_mode_change_updates_ui(
    annotator: PdQtAnnotator,
    mocker: MagicMock
) -> None:
    """
    Verify that changing the dropdown text triggers the expected mode.

    Parameters
    ----------
    annotator : PdQtAnnotator
        The initialized annotator window fixture.
    """
    # Prevent the UI from attempting to redraw missing test
    # data during fallback
    mocker.patch.object(annotator, "update")

    annotator.mode_drop_down.setCurrentText("Exercise")
    assert annotator.annotator_mode == AnnotatorMode.EXERCISE
