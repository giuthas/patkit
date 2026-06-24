"""Integration tests for keyboard hotkeys and focus routing."""

from unittest.mock import MagicMock
from PyQt6.QtCore import Qt
from pytestqt.plugin import QtBot

from patkit.qt_annotator import PdQtAnnotator


def test_modifiers_propagate_from_canvas(
    qtbot: QtBot,
    annotator: PdQtAnnotator
) -> None:
    """
    Verify that key presses on the canvas bubble up to the main window.

    This guards against focus stealing bugs where the child widget consumes
    keyboard events instead of letting the annotator handle them.

    Parameters
    ----------
    bot : QtBot
        The Qt testing bot.
    annotator : PdQtAnnotator
        The active, initialized annotator window fixture.
    """
    # Explicitly force focus onto the plot canvas
    canvas = annotator.centralWidget().findChild(
        type=annotator.plot_controller.canvas.__class__
    )
    canvas.setFocus()
    assert canvas.hasFocus() is True

    # Simulate OS-level key press targeted at the focused canvas
    qtbot.keyPress(widget=canvas, key=Qt.Key.Key_Shift)

    # If the focus policy is correct, the event bubbles to the main window
    assert annotator.shift_is_held is True

    qtbot.keyRelease(widget=canvas, key=Qt.Key.Key_Shift)
    assert annotator.shift_is_held is False


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

    # Simulate holding Alt
    annotator.alt_is_held = True

    qtbot.keyPress(widget=annotator, key=Qt.Key.Key_I)
    annotator.zoom_in.assert_called_once()

    qtbot.keyPress(widget=annotator, key=Qt.Key.Key_O)
    annotator.zoom_out.assert_called_once()

    qtbot.keyPress(widget=annotator, key=Qt.Key.Key_Left)
    annotator.pan.assert_called_once_with(left=True)

    qtbot.keyPress(widget=annotator, key=Qt.Key.Key_Right)
    annotator.pan.assert_called_with(left=False)
