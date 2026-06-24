"""Tests for the core rendering logic in PlotController."""

from unittest.mock import MagicMock
import pytest

import numpy as np

from patkit.constants import AnnotatorMode, ExerciseMode, GuiImageType
from patkit.gui.plot_controller import PlotController


@pytest.fixture
def rendering_controller(
    mocker: MagicMock,
    plot_controller: PlotController
) -> PlotController:
    """
    Provide a PlotController with expensive matplotlib routines mocked.

    Parameters
    ----------
    mocker : MagicMock
        The pytest mocker.
    plot_controller : PlotController
        The baseline plot controller fixture.

    Returns
    -------
    PlotController
        The controller ready for rendering tests.
    """
    mocker.patch("patkit.gui.plot_controller.plot_wav")
    mocker.patch("patkit.gui.plot_controller.plot_spectrogram")

    # We must patch boundary animator to avoid Qt signal connections
    mocker.patch("patkit.gui.plot_controller.BoundaryAnimator")
    mocker.patch("patkit.gui.plot_controller.MultiCursor")

    return plot_controller


def test_draw_plots_aborts_without_audio(
    rendering_controller: PlotController
) -> None:
    """
    Verify rendering handles missing audio gracefully.

    Parameters
    ----------
    rendering_controller : PlotController
        The PlotController fixture.
    """
    mock_recording = MagicMock()
    mock_recording.excluded = False
    mock_recording.modalities = {}  # No 'MonoAudio'

    rendering_controller.setup_axes = MagicMock()

    # We inject dummy data axes so the title setter doesn't natively crash
    mock_axis = MagicMock()
    rendering_controller.data_axes = [mock_axis]

    rendering_controller.draw_plots(
        recording=mock_recording,
        patgrid=[],
        xlim=(0.0, 1.0),
        mode=AnnotatorMode.ANALYSE,
        exercise_mode=ExerciseMode.ANSWER,
        title="Test Recording"
    )

    mock_axis.set_title.assert_called_once_with(
        "Test Recording\nNOTE: Audio missing."
    )


def test_draw_plots_with_audio_and_tiers(
    rendering_controller: PlotController
) -> None:
    """
    Verify standard drawing pipeline sets up ticks and dispatchers correctly.

    Parameters
    ----------
    rendering_controller : PlotController
        The PlotController fixture.
    """
    # Setup mock data config to enforce 'wav' plotting
    rendering_controller.gui_config.data_axes = {"wav": MagicMock()}
    rendering_controller.gui_config.xlim = (0.0, 2.0)

    mock_audio = MagicMock()
    mock_audio.go_signal = 0.0
    mock_audio.data = np.array([0.1, 0.2])
    mock_audio.timevector = np.array([0.0, 1.0])

    mock_recording = MagicMock()
    mock_recording.excluded = False
    mock_recording.modalities = {"MonoAudio": mock_audio}
    mock_recording.annotations = {
        "selected_time": -1,
        "selected_frequency": -1
    }

    # Execute
    rendering_controller.draw_plots(
        recording=mock_recording,
        patgrid=rendering_controller.main_window.session.recordings[0].patgrid,
        xlim=(0.0, 2.0),
        mode=AnnotatorMode.ANALYSE,
        exercise_mode=ExerciseMode.ANSWER,
        title="Test Draw"
    )

    # Verification
    # 1. Ensure animators were attached to the intersecting boundaries
    assert len(rendering_controller.animators) == 3

    # 2. Ensure bottom-most tier axis retains tick labels for Multicursor
    bottom_axis = rendering_controller.tier_axes[-1]
    bottom_axis.xaxis.set_tick_params.assert_called_with(
        bottom=True, labelbottom=True
    )

    # 3. Ensure the multi-cursor sync logic fired
    assert rendering_controller.original_xticks is not None


def test_draw_ultra_frame_aborts_without_ultrasound(
    plot_controller: PlotController
) -> None:
    """
    Verify ultrasound rendering exits natively if data is missing.

    Parameters
    ----------
    plot_controller : PlotController
        The baseline plot controller fixture.
    """
    mock_recording = MagicMock()
    mock_recording.modalities = {}

    result = plot_controller.draw_ultra_frame(
        recording=mock_recording,
        image_type=GuiImageType.FRAME
    )

    assert result is False


def test_draw_ultra_frame_with_data(
    plot_controller: PlotController
) -> None:
    """
    Verify ultrasound image data is extracted and passed to imshow.

    Parameters
    ----------
    plot_controller : PlotController
        The baseline plot controller fixture.
    """
    mock_ultra = MagicMock()
    mock_ultra.interpolated_image.return_value = MagicMock(shape=(10, 20))

    mock_recording = MagicMock()
    mock_recording.modalities = {"RawUltrasound": mock_ultra}
    mock_recording.annotations = {"frame_selection_index": 5}

    plot_controller.ultra_axes = MagicMock()

    result = plot_controller.draw_ultra_frame(
        recording=mock_recording,
        image_type=GuiImageType.FRAME
    )

    assert result is True
    mock_ultra.interpolated_image.assert_called_once_with(5)
    plot_controller.ultra_axes.imshow.assert_called_once()
