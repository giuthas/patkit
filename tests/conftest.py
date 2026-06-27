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
"""Pytest configuration and shared fixtures for PATKIT GUI testing."""

from pathlib import Path
import pytest

import numpy as np
from PyQt6.QtWidgets import QDialog
from pytestqt.plugin import QtBot
from unittest.mock import MagicMock

from patkit.constants import AnnotatorMode, GuiColorScheme
from patkit.data_structures import Recording, Session
from patkit.gui import NewExerciseDialog, NewAnswerDialog, PlotController
from patkit.patgrid import PatGrid
from patkit.qt_annotator import PdQtAnnotator

TEXTGRID_CONTENT = """File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0.0
xmax = 3.76155102041
tiers? <exists>
size = 2
item []:
    item [1]:
        class = "IntervalTier"
        name = "word"
        xmin = 0.0
        xmax = 3.76155102041
        intervals: size = 3
            intervals [1]:
                xmin = 0.0
                xmax = 2.48151102041
                text = ""
            intervals [2]:
                xmin = 2.48151102041
                xmax = 2.70455102041
                text = "ri"
            intervals [3]:
                xmin = 2.70455102041
                xmax = 3.76155102041
                text = ""
    item [2]:
        class = "IntervalTier"
        name = "segment"
        xmin = 0.0
        xmax = 3.76155102041
        intervals: size = 5
            intervals [1]:
                xmin = 0.0
                xmax = 1.76138178001
                text = ""
            intervals [2]:
                xmin = 1.76138178001
                xmax = 2.48151102041
                text = "beep"
            intervals [3]:
                xmin = 2.48151102041
                xmax = 2.54368102041
                text = "r"
            intervals [4]:
                xmin = 2.54368102041
                xmax = 2.70455102041
                text = "i"
            intervals [5]:
                xmin = 2.70455102041
                xmax = 3.76155102041
                text = ""
"""


@pytest.fixture(scope="session")
def dummy_textgrid_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Create a temporary TextGrid file for the test session.
    """
    file_path = tmp_path_factory.mktemp("data") / "dummy.TextGrid"
    file_path.write_text(TEXTGRID_CONTENT, encoding="utf-8")
    return file_path


@pytest.fixture
def real_patgrid(dummy_textgrid_file: Path) -> PatGrid:
    """
    Parse the dummy TextGrid file into a real patgrid object.
    """
    return PatGrid(dummy_textgrid_file)


@pytest.fixture
def mock_config() -> MagicMock:
    """
    Create a robust mock Configuration object mimicking Pydantic models.

    Returns
    -------
    MagicMock
        The mocked configuration object.
    """
    config = MagicMock()

    # --- DataConfig ---
    data_config = MagicMock()
    data_config.epsilon = 0.01
    config.data_config = data_config

    # --- GuiConfig ---
    gui_config = MagicMock()

    # 1. Scalar settings
    gui_config.color_scheme = GuiColorScheme.LIGHT
    gui_config.default_font_size = 10
    gui_config.xlim = None
    gui_config.auto_xlim = True
    gui_config.display_image_info = True
    gui_config.display_curve_values = True
    gui_config.pervasive_tiers = []  # Must be an iterable list, not a mock

    # 2. Mocking the plotted_modality_names method
    gui_config.plotted_modality_names.return_value = {"MonoAudio"}

    # 3. Height Ratios setup
    height_ratios = MagicMock()
    height_ratios.data_axes = 1
    height_ratios.tier_axes = 1
    gui_config.data_and_tier_height_ratios = height_ratios

    # 4. General axes parameters
    # (Set to None to skip complex fallbacks in tests)
    gui_config.general_axes_params = None

    # 5. Data Axes definitions (Mimics dict[str, AxesDefinition])
    axes_def = MagicMock()
    axes_def.sharex = False
    axes_def.ylim = None
    axes_def.auto_ylim = True
    axes_def.modalities = ["MonoAudio"]
    axes_def.colors_in_sequence = False
    axes_def.y_offset = 0
    axes_def.normalisation = "none"
    axes_def.modality_names = ["Audio"]
    axes_def.mark_peaks = False
    axes_def.legend = False

    gui_config.data_axes = {"wav": axes_def}

    # 6. Properties
    gui_config.number_of_data_axes = 1

    config.gui_config = gui_config

    return config


@pytest.fixture
def mock_session(real_patgrid) -> MagicMock:
    """
    Create a mock Session object populated with a dummy recording.

    Returns
    -------
    MagicMock
        The mocked session object containing a minimal Recording structure.
    """
    session = MagicMock(spec=Session)
    session.exercise = None

    recording = MagicMock(spec=Recording)

    # Set attributes required by add_items_to_database_view and plots
    recording.basename = "test_recording"
    recording.excluded = False

    audio_mock = MagicMock()
    audio_mock.go_signal = 0.0
    audio_mock.data = np.array([0.1, 0.2])
    audio_mock.timevector = np.array([0.0, 1.0])
    recording.modalities = {"MonoAudio": audio_mock}

    # Tell the mock how to behave when the controller
    # does `if "MonoAudio" in recording:`
    recording.__contains__.side_effect = (
        lambda key: key in recording.modalities
    )
    recording.__getitem__.side_effect = lambda key: recording.modalities[key]

    recording.patgrid = real_patgrid
    recording.annotations = {"selected_time": 0.5, "selected_frequency": -1}

    metadata = MagicMock()
    metadata.prompt = "Dummy prompt text"
    recording.metadata = metadata

    # Mock list-like iteration and indexing behaviour for the session
    recordings_list = [recording]
    session.recordings = recordings_list
    session.__len__ = lambda self: len(recordings_list)
    session.__iter__ = lambda self: iter(recordings_list)
    session.__getitem__ = lambda self, idx: recordings_list[idx]

    return session


@pytest.fixture
def annotator(
    qtbot: QtBot,
    mocker: MagicMock,
    mock_session: MagicMock,
    mock_config: MagicMock,
) -> PdQtAnnotator:
    """
    Initialize and yield a PdQtAnnotator instance for integration testing.

    Parameters
    ----------
    bot : QtBot
        The pytest-qt plugin bot for handling the Qt event loop.
    mock_session : MagicMock
        The mocked data session fixture.
    mock_config : MagicMock
        The mocked configuration fixture.

    Yields
    ------
    PdQtAnnotator
        The active, initialized annotator window instance.
    """
    # 1. Stop accidental dialogs from freezing the test suite!
    # If ANY test triggers these dialogs, they will instantly
    # return "Rejected" (Cancel)
    mocker.patch.object(NewExerciseDialog, "exec",
                        return_value=QDialog.DialogCode.Rejected)
    mocker.patch.object(NewAnswerDialog, "exec",
                        return_value=QDialog.DialogCode.Rejected)

    widget = PdQtAnnotator(
        session=mock_session,
        display_tongue=False,
        config=mock_config,
        annotator_mode=AnnotatorMode.ANALYSE,
    )
    qtbot.addWidget(widget=widget)

    yield widget

    widget.close()


@pytest.fixture
def plot_controller(
    mocker: MagicMock,
    mock_config: MagicMock,
    mock_session: MagicMock,
) -> PlotController:
    """Shared PlotController fixture with mocked Matplotlib canvas."""
    mocker.patch("patkit.gui.plot_controller.Figure")
    mocker.patch("patkit.gui.plot_controller.FigureCanvas")
    mocker.patch("matplotlib.pyplot.style.use")

    mock_main_window = MagicMock()
    mock_main_window.session = mock_session

    controller = PlotController(
        data_config=mock_config.data_config,
        gui_config=mock_config.gui_config,
        main_window=mock_main_window
    )
    return controller
