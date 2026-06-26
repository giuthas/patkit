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
"""Integration tests for keyboard hotkeys and focus routing."""

from unittest.mock import MagicMock
from PyQt6.QtCore import Qt
from pytestqt.plugin import QtBot

from patkit.qt_annotator import PdQtAnnotator


# TODO 1.0: Try to get a working version for testing focus stealing does not
# divert key presses from keyPressEvent, or just move to Qt native hotkeys
# which is probably a better idea anyhow.
# def test_modifiers_propagate_from_canvas(
#     qtbot: QtBot,
#     annotator: PdQtAnnotator
# ) -> None:
#     """
#     Verify that key presses on the canvas bubble up to the main window.

#     This guards against focus stealing bugs where the child widget consumes
#     keyboard events instead of letting the annotator handle them.

#     Parameters
#     ----------
#     bot : QtBot
#         The Qt testing bot.
#     annotator : PdQtAnnotator
#         The active, initialized annotator window fixture.
#     """
#     # Explicitly force focus onto the plot canvas
#     canvas = annotator.centralWidget().findChild(
#         annotator.plot_controller.canvas.__class__
#     )
#     canvas.setFocus()
#     assert canvas.hasFocus() is True

#     # Simulate OS-level key press targeted at the focused canvas
#     qtbot.keyPress(canvas, Qt.Key.Key_Shift)

#     # If the focus policy is correct, the event bubbles to the main window
#     assert annotator.shift_is_held is True

#     qtbot.keyRelease(widget=canvas, key=Qt.Key.Key_Shift)
#     assert annotator.shift_is_held is False


def test_alt_hotkeys_trigger_actions(
    qtbot: QtBot,
    annotator: PdQtAnnotator
) -> None:
    """
    Verify that Alt + Key combos trigger the correct UI methods.

    Parameters
    ----------
    bot : QtBot
        The Qt testing bot.
    annotator : PdQtAnnotator
        The active, initialized annotator window fixture.
    """
    annotator.zoom_in = MagicMock()
    annotator.zoom_out = MagicMock()
    annotator.pan = MagicMock()

    qtbot.keyPress(annotator, Qt.Key.Key_I,
                   modifier=Qt.KeyboardModifier.AltModifier)
    annotator.zoom_in.assert_called_once()

    qtbot.keyPress(annotator, Qt.Key.Key_O,
                   modifier=Qt.KeyboardModifier.AltModifier)
    annotator.zoom_out.assert_called_once()

    qtbot.keyPress(annotator, Qt.Key.Key_Left,
                   modifier=Qt.KeyboardModifier.AltModifier)
    annotator.pan.assert_called_once_with(left=True)

    qtbot.keyPress(annotator, Qt.Key.Key_Right,
                   modifier=Qt.KeyboardModifier.AltModifier)
    annotator.pan.assert_called_with(left=False)
