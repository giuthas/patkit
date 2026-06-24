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
    assert annotator.mode == AnnotatorMode.ANALYSE
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
    assert annotator.mode == AnnotatorMode.EXERCISE
