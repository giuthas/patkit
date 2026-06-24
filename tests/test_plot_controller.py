"""Tests for the PlotController functionality in the PATKIT GUI."""

from unittest.mock import MagicMock
import pytest
from patkit.constants import GuiColorScheme
from patkit.gui.plot_controller import PlotController


def test_to_annotator_mode_light(plot_controller: PlotController) -> None:
    """Test background color change for annotator mode in light theme."""
    plot_controller.to_annotator_mode(gui_color_mode=GuiColorScheme.LIGHT)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "white"
    )


def test_to_annotator_mode_dark(plot_controller: PlotController) -> None:
    """Test background color change for annotator mode in dark theme."""
    plot_controller.to_annotator_mode(gui_color_mode=GuiColorScheme.DARK)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "black"
    )


def test_to_exercise_mode_light(plot_controller: PlotController) -> None:
    """Test background color change for exercise mode in light theme."""
    plot_controller.to_exercise_mode(gui_color_mode=GuiColorScheme.LIGHT)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "#e6ffe9"
    )


def test_to_exercise_mode_dark(plot_controller: PlotController) -> None:
    """Test background color change for exercise mode in dark theme."""
    plot_controller.to_exercise_mode(gui_color_mode=GuiColorScheme.DARK)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "#001202"
    )


def test_to_example_mode_light(plot_controller: PlotController) -> None:
    """Test background color change for example mode in light theme."""
    plot_controller.to_example_mode(gui_color_mode=GuiColorScheme.LIGHT)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "#e7eaff"
    )


def test_to_example_mode_dark(plot_controller: PlotController) -> None:
    """Test background color change for example mode in dark theme."""
    plot_controller.to_example_mode(gui_color_mode=GuiColorScheme.DARK)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "#000212"
    )


def test_to_answer_mode_light(plot_controller: PlotController) -> None:
    """Test background color change for answer mode in light theme."""
    plot_controller.to_answer_mode(gui_color_mode=GuiColorScheme.LIGHT)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "#e6ffe9"
    )


def test_to_answer_mode_dark(plot_controller: PlotController) -> None:
    """Test background color change for answer mode in dark theme."""
    plot_controller.to_answer_mode(gui_color_mode=GuiColorScheme.DARK)
    plot_controller.figure.patch.set_facecolor.assert_called_once_with(
        "#001202"
    )


def test_invalid_color_scheme(plot_controller: PlotController) -> None:
    """Test that an unknown color scheme raises a ValueError."""
    with pytest.raises(expected_exception=ValueError):
        plot_controller.to_annotator_mode(gui_color_mode="INVALID")


def test_setup_axes(plot_controller: PlotController) -> None:
    """Test that setup_axes clears and rebuilds subplots properly."""
    plot_controller.setup_axes()

    plot_controller.figure.clear.assert_called_once()
    plot_controller.figure.add_gridspec.assert_called_once_with(
        nrows=2,
        ncols=1,
        hspace=0,
        wspace=0,
        height_ratios=[1, 1],
    )
    assert len(plot_controller.data_axes) == 1
    plot_controller.canvas.draw_idle.assert_called_once()


def test_clear_axes(plot_controller: PlotController) -> None:
    """Test that clear_axes clears all data and tier axes."""
    mock_axis_1 = MagicMock()
    mock_axis_2 = MagicMock()
    plot_controller.data_axes = [mock_axis_1]
    plot_controller.tier_axes = [mock_axis_2]

    plot_controller.clear_axes()

    mock_axis_1.cla.assert_called_once()
    mock_axis_2.cla.assert_called_once()


def test_update_selection_cursors_active(
    plot_controller: PlotController
) -> None:
    """Test selection cursors and ticks when selection is active."""
    mock_recording = MagicMock()
    mock_recording.annotations = {
        "selected_time": 1.5,
        "selected_frequency": 5000.0,
    }

    mock_axis = MagicMock()
    mock_axis.get_xticks.return_value = [0.0, 1.0, 2.0, 3.0]
    mock_axis.get_yticks.return_value = [10.0, 20.0]

    plot_controller.data_axes = [mock_axis]
    plot_controller.original_xticks = [0.0, 1.0, 2.0, 3.0]
    plot_controller.original_yticks = {mock_axis: [10.0, 20.0]}

    mock_label_1 = MagicMock()
    mock_label_2 = MagicMock()
    mock_axis.get_xticklabels.return_value = [mock_label_1, mock_label_2]
    mock_axis.get_yticklabels.return_value = []
    mock_axis.yaxis.get_ticklines.return_value = []
    mock_axis.get_lines.return_value = []

    plot_controller.gui_config.data_axes = {"spectrogram": MagicMock()}

    plot_controller.update_selection_cursors(recording=mock_recording)

    mock_axis.set_xticks.assert_called()
    mock_axis.axvline.assert_called()
    plot_controller.canvas.draw.assert_called_once()


def test_update_selection_cursors_inactive(
    plot_controller: PlotController
) -> None:
    """Test selection cursors cleanup when selection is disabled."""
    mock_recording = MagicMock()
    mock_recording.annotations = {
        "selected_time": -1.0,
        "selected_frequency": -1.0,
    }

    mock_axis = MagicMock()
    plot_controller.data_axes = [mock_axis]
    plot_controller.original_xticks = [0.0, 1.0, 2.0, 3.0]
    plot_controller.original_yticks = {mock_axis: [10.0, 20.0]}

    mock_label = MagicMock()
    mock_axis.get_xticklabels.return_value = [mock_label]

    plot_controller.update_selection_cursors(recording=mock_recording)

    mock_axis.set_xticks.assert_called_with([1.0, 2.0])
    plot_controller.canvas.draw.assert_called_once()


def test_update_playback_cursor(plot_controller: PlotController) -> None:
    """Test updating the animated playback cursor line positions."""
    mock_line = MagicMock()
    plot_controller.playback_cursor_lines = [mock_line]
    plot_controller.playback_background = "dummy_bg"

    plot_controller.update_playback_cursor(current_time=2.4)

    mock_line.set_xdata.assert_called_once_with([2.4, 2.4])
    mock_line.set_visible.assert_called_once_with(True)
    plot_controller.canvas.blit.assert_called_once()


def test_hide_playback_cursor(plot_controller: PlotController) -> None:
    """Test hiding playback cursor and restoring multicursor state."""
    mock_line = MagicMock()
    plot_controller.playback_cursor_lines = [mock_line]

    plot_controller.hide_playback_cursor()

    mock_line.set_animated.assert_called_once_with(False)
    mock_line.set_visible.assert_called_once_with(False)
    assert plot_controller.playback_background is None
    plot_controller.canvas.draw.assert_called_once()
