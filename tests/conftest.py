"""Pytest configuration and shared fixtures for PATKIT GUI testing."""

from unittest.mock import MagicMock
import pytest
from pytestqt.plugin import QtBot

from patkit.constants import AnnotatorMode, GuiColorScheme
from patkit.data_structures import Recording, Session
from patkit.gui.plot_controller import PlotController
from patkit.qt_annotator import PdQtAnnotator


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
    qtbot: QtBot,
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
