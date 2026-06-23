"""Pytest configuration and shared fixtures for PATKIT GUI testing."""

from unittest.mock import MagicMock
import pytest
from pytestqt.plugin import QtBot

from patkit.configuration import Configuration, DataConfig, GuiConfig
from patkit.constants import AnnotatorMode, GuiColorScheme
from patkit.data_structures import Recording, Session
from patkit.qt_annotator import PdQtAnnotator


@pytest.fixture
def mock_config() -> MagicMock:
    """
    Create a mock Configuration object with standard nested attributes.

    Returns
    -------
    MagicMock
        The mocked configuration object.
    """
    config = MagicMock(spec=Configuration)
    data_config = MagicMock(spec=DataConfig)
    gui_config = MagicMock(spec=GuiConfig)

    # Setup necessary configuration values for GUI boot
    gui_config.color_scheme = GuiColorScheme.LIGHT
    gui_config.default_font_size = 10
    gui_config.number_of_data_axes = 1
    gui_config.data_axes = {}
    gui_config.general_axes_params = None

    # Setup standard height ratios expected by the PlotController
    height_ratios = MagicMock()
    height_ratios.data_axes = [1]
    height_ratios.tier_axes = [1]
    gui_config.data_and_tier_height_ratios = height_ratios

    config.data_config = data_config
    config.gui_config = gui_config

    return config


@pytest.fixture
def mock_session() -> MagicMock:
    """
    Create a mock Session object populated with a dummy recording.

    Returns
    -------
    MagicMock
        The mocked session object containing a minimal Recording structure.
    """
    session = MagicMock(spec=Session)
    recording = MagicMock(spec=Recording)

    # Set attributes required by add_items_to_database_view and plots
    recording.basename = "test_recording"
    recording.excluded = False
    recording.modalities = {"MonoAudio": MagicMock()}
    recording.patgrid = MagicMock()
    recording.annotations = {"selected_time": 0.5}

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
    bot: QtBot,
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
    widget = PdQtAnnotator(
        session=mock_session,
        display_tongue=False,
        config=mock_config,
        annotator_mode=AnnotatorMode.ANALYSE,
    )
    bot.addWidget(widget=widget)

    yield widget

    widget.close()
