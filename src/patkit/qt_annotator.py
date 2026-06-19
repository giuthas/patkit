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
This is the main GUI class for patkit.
"""

import csv
import logging
import sys
from contextlib import closing
from copy import deepcopy
from pathlib import Path

import numpy as np


from PyQt6 import QtWidgets
from PyQt6.QtCore import (
    QCoreApplication, QItemSelectionModel, QModelIndex, Qt
)
from PyQt6.QtGui import (
    QGuiApplication,
    QIntValidator,
    QKeySequence,
    QShortcut,
)
from PyQt6.QtWidgets import (
    QFileDialog, QMainWindow
)
from qbstyles import mpl_style

from patkit.configuration import Configuration
from patkit.constants import (
    AnnotatorMode, ExerciseMode, GuiColorScheme, GuiImageType, OpenPathType
)
from patkit.data_structures import Exercise, Session
from patkit.export import (
    export_aggregate_image_and_meta,
    export_distance_matrix_and_meta,
    export_session_and_recording_meta,
    export_ultrasound_frame_and_meta,
)
from patkit.gui import (
    AudioPlayer,
    ImageSaveDialog, ListSaveDialog,
    ListSelectionDialog, PlotController,
    ReplaceDialog, UiMainWindow,
)
from patkit.initialise import initialise_config, initialise_patkit
from patkit.path_resolution import get_manifest_scenarios, resolve_open_path
from patkit.save_and_load import (
    load_exercise, save_recording_session
)
from patkit.ui_callbacks import UiCallbacks

_logger = logging.getLogger('patkit.qt_annotator')


def setup_qtannotator_ui_callbacks():
    """
    Register UI callback functions.
    """
    UiCallbacks.register_overwrite_confirmation_callback(
        ReplaceDialog.confirm_overwrite)


class PdQtAnnotator(QMainWindow, UiMainWindow):
    """
    Qt_Annotator_Window is a GUI class for annotating PD curves.

    The annotator works with PD curves and allows
    selection of a single points (labelled as pdOnset in the saved file).
    The GUI also displays the waveform, and if TextGrids
    are provided, the acoustic segment boundaries.
    """

    default_categories = ['Stable', 'Hesitation', 'Chaos', 'No data',
                          'Not set']

    default_tongue_positions = ['High', 'Low', 'Other / Not visible']

    def __init__(
            self,
            session: Session,
            display_tongue: bool,
            config: Configuration,
            xlim: tuple[float, float] = (-0.25, 1.5),
            categories: list[str] | None = None,
            annotator_mode: AnnotatorMode = AnnotatorMode.ANALYSE,
    ):
        super().__init__()
        self.kymography_clicker = None
        self.setupUi(self)
        setup_qtannotator_ui_callbacks()

        self.session = session
        self.recordings = session.recordings
        self.index = 0
        self.patgrid = self.current.patgrid

        self.max_index = len(self.recordings)

        self.display_tongue = display_tongue

        self.mode_drop_down.setCurrentText(annotator_mode.value)
        self.mode = annotator_mode
        self.exercise_mode = ExerciseMode.ANSWER
        if annotator_mode is AnnotatorMode.EXERCISE:
            self.exercise = Exercise(session)
        else:
            self.exercise = None

        self.data_config = config.data_config
        self.gui_config = config.gui_config

        self.add_items_to_database_view(session)

        if categories is None:
            self.categories = PdQtAnnotator.default_categories
        else:
            self.categories = categories
        self.tongue_positions = PdQtAnnotator.default_tongue_positions
        self._add_annotations()

        self.gui_mode = config.gui_config.color_scheme
        self._update_color_mode()

        QGuiApplication.styleHints().colorSchemeChanged.connect(
            self.on_color_scheme_changed)

        #
        # Menu actions and shortcuts
        #
        self.close_window_shortcut = QShortcut(
            QKeySequence(self.tr("Ctrl+W", "File|Quit")), self)
        self.close_window_shortcut.activated.connect(self.quit)

        # Image selection logic hookups
        self.menu_select_small_action_group.triggered.connect(
            self.image_updater)
        self.image_type = GuiImageType.MEAN_IMAGE

        # self.action_select_kymography_line = QAction(
        #     text="Select kymography sample line", parent=self.menu_plot)
        # self.menu_plot.addAction(self.action_select_kymography_line)

        self.action_open.triggered.connect(self.open)
        self.action_save_all.triggered.connect(self.save_all)
        self.action_save_current_textgrid.triggered.connect(self.save_textgrid)
        self.action_save_all_textgrids.triggered.connect(
            self.save_all_textgrids)

        self.mode_drop_down.currentTextChanged.connect(
            self.mode_selection_changed)
        self.exercise_drop_down.currentTextChanged.connect(
            self.exercise_selection_changed)

        self.action_create_exercise.triggered.connect(
            self.create_exercise)
        self.action_open_exercise.triggered.connect(self.open_exercise)
        self.action_open_answer.triggered.connect(self.open_answer)
        self.action_save_answer.triggered.connect(self.save_answer)
        self.action_compare_to_example.triggered.connect(
            self.compare_to_example)
        self.action_show_example.triggered.connect(self.show_example)

        self.action_export_aggregate_images.triggered.connect(
            self.export_aggregate_image)
        self.action_export_annotations_and_metadata.triggered.connect(
            self.export_annotations_and_metadata)
        self.action_export_distance_matrices.triggered.connect(
            self.export_distance_matrix)
        self.action_export_main_figure.triggered.connect(self.export_figure)
        self.action_export_ultrasound_frame.triggered.connect(
            self.export_ultrasound_frame)

        self.action_next.triggered.connect(self.next)
        self.action_previous.triggered.connect(self.prev)

        self.action_next_frame.triggered.connect(self.next_frame)
        self.action_previous_frame.triggered.connect(self.previous_frame)

        self.action_quit.triggered.connect(self.quit)

        # Go to recording
        go_validator = QIntValidator(1, self.max_index + 1, self)
        self.go_to_line_edit.setValidator(go_validator)
        self.goButton.clicked.connect(self.go_to_callback)
        self.previous_button.clicked.connect(self.prev)
        self.next_button.clicked.connect(self.next)
        self.go_to_line_edit.returnPressed.connect(self.go_to_callback)

        # PD categories
        # TODO 1.0: these could be optional instead of the below ones
        # self.categoryRB_1.toggled.connect(self.pd_category_cb)
        # self.categoryRB_2.toggled.connect(self.pd_category_cb)
        # self.categoryRB_3.toggled.connect(self.pd_category_cb)
        # self.categoryRB_4.toggled.connect(self.pd_category_cb)
        # self.categoryRB_5.toggled.connect(self.pd_category_cb)

        # Tongue position annotation buttons.
        # self.positionRB_1.toggled.connect(self.tongue_position_cb)
        # self.positionRB_2.toggled.connect(self.tongue_position_cb)
        # self.positionRB_3.toggled.connect(self.tongue_position_cb)
        # self.position_rbs = {
        #     self.positionRB_1.text(): self.positionRB_1,
        #     self.positionRB_2.text(): self.positionRB_2,
        #     self.positionRB_3.text(): self.positionRB_3
        # }

        # Audio playback setup
        self.audio_player = AudioPlayer(self)
        self.play_controls.play.connect(self.audio_player.play)
        self.play_controls.pause.connect(self.audio_player.pause)
        self.play_controls.stop.connect(self.audio_player.stop)
        self.play_controls.rewind.connect(self.rewind)

        self.shift_is_held = False
        self.ctrl_is_held = False
        self.alt_is_held = False
        self.alt_gr_is_held = False

        self.xlim = xlim

        # Plot controller setup
        self.plot_controller = PlotController(
            data_config=self.data_config,
            gui_config=self.gui_config,
            parent=self
        )

        # Add the canvases to their respective Qt Layouts
        self.mplWindowVerticalLayout.addWidget(self.plot_controller.canvas)
        self.verticalLayout_6.addWidget(self.plot_controller.ultra_canvas)

        # Connect tracking events
        self.audio_player.position_changed.connect(
            self.plot_controller.update_playback_cursor)
        self.audio_player.playback_stopped.connect(
            self.plot_controller.hide_playback_cursor)
        self.audio_player.playback_paused.connect(
            self._sync_selected_time)

        if not self.current.excluded:
            self._set_audio_for_player()
            self.update()  # Let the update method trigger the initial draw
        else:
            self.display_exclusion()

        self.plot_controller.figure.align_ylabels()

        self.mode_selection_changed(self.mode.value)
        self.image_updater()
        self.showMaximized()
        self.plot_controller.ultra_canvas.draw_idle()
        self.update()

    def _update_color_mode(self) -> None:
        match self.gui_config.color_scheme:
            case GuiColorScheme.DARK:
                self.change_to_dark()
            case GuiColorScheme.LIGHT:
                self.change_to_light()
            case GuiColorScheme.FOLLOW_SYSTEM:
                match QGuiApplication.styleHints().colorScheme():
                    case Qt.ColorScheme.Dark:
                        self.gui_config.color_scheme = GuiColorScheme.DARK
                        self.change_to_dark()
                    case Qt.ColorScheme.Light:
                        self.gui_config.color_scheme = GuiColorScheme.LIGHT
                        self.change_to_light()
                    case _:
                        self.gui_config.color_scheme = GuiColorScheme.DARK
                        self.change_to_dark()
                        _logger.warning(
                            "Unknown system level color scheme. "
                            "So just setting mode to dark.")
            case _:
                _logger.warning(
                    "Unrecognised gui style %s.",
                    self.gui_config.color_scheme)

    def change_to_dark(self):
        """Activate dark mode."""
        self.gui_mode = GuiColorScheme.DARK
        mpl_style(dark=True)

    def change_to_light(self):
        """Activate light mode."""
        self.gui_mode = GuiColorScheme.LIGHT
        mpl_style(dark=False)

    @property
    def current(self):
        """Current recording at index."""
        return self.recordings[self.index]

    @property
    def default_annotations(self):
        """List default annotations and their default values as a dict."""
        return {
            'pdCategory': self.categories[-1],
            'tonguePosition': self.tongue_positions[-1],
            'selected_time': -1.0,
            'selection_index': -1,
            'frame_selection_index': -1,
            'selected_frequency': -1,
        }

    def _add_annotations(self):
        """Add the annotations."""
        for recording in self.recordings:
            if recording.annotations:
                recording.annotations = dict(
                    list(self.default_annotations.items()) +
                    list(recording.annotations.items()))
            else:
                recording.annotations = deepcopy(self.default_annotations)

    def _get_title(self):
        """
        Private helper function for generating the title.
        """
        text = 'Recording: ' + str(self.index + 1) + '/' + str(self.max_index)
        text += ', prompt: ' + self.current.metadata.prompt
        return text

    def _get_long_title(self):
        """
        Private helper function for generating a longer title for a figure.
        """
        text = 'Recording: ' + str(self.index + 1) + '/' + str(self.max_index)
        text += ', Speaker: ' + str(self.current.metadata.participant_id)
        text += ', prompt: ' + self.current.metadata.prompt
        return text

    def _release_modality_memory(self):
        if 'RawUltrasound' in self.current.modalities:
            self.current.modalities['RawUltrasound'].data = None

    def _set_audio_for_player(self) -> None:
        """Pass the current audio data to the audio player."""
        if 'MonoAudio' in self.current.modalities:
            mono_audio = self.current['MonoAudio'].modality_data
            self.audio_player.set_audio(
                audio_data=mono_audio.data,
                sampling_rate=mono_audio.sampling_rate
            )

    def _sync_selected_time(self, current_position: float) -> None:
        """
        Sync the global annotation state with the audio player's position.

        Parameters
        ----------
        current_position : float
            The time in seconds where playback was paused.
        """
        self.current.annotations['selected_time'] = current_position
        self.update()

    def clear_axes(self):
        """Clear data axes of this annotator."""
        for axes in self.data_axes:
            axes.cla()

    def update(self) -> None:
        """Updates the graphs but not the buttons."""
        if (
            self.mode is AnnotatorMode.EXERCISE and
            self.exercise_mode is ExerciseMode.ANSWER
        ):
            self.patgrid = self.exercise.current_answer[self.index]
        else:
            self.patgrid = self.current.patgrid

        self.plot_controller.draw_plots(
            recording=self.current,
            patgrid=self.patgrid,
            xlim=self.xlim,
            mode=self.mode,
            exercise_mode=self.exercise_mode,
            title=self._get_long_title(),
        )
        self.plot_controller.update_multicursor()
        self.plot_controller.canvas.draw_idle()

        if self.display_tongue:
            _logger.debug("Drawing ultra frame in update")
            has_ultra_data = self.plot_controller.draw_ultra_frame(
                recording=self.current,
                image_type=self.image_type
            )
            self.plot_controller.ultra_canvas.draw_idle()
            self.action_export_ultrasound_frame.setEnabled(has_ultra_data)

    def update_ui(self):
        """
        Updates parts of the UI outwith the graphs.
        """
        # Annotation radio buttons.
        # position_annotation = self.current.annotations['tonguePosition']
        # if position_annotation in self.position_rbs:
        #     button_to_activate = self.position_rbs[position_annotation]
        #     button_to_activate.setChecked(True)

        self.go_to_line_edit.setText(str(self.index + 1))

        qt_index = self.database_view.model().index(self.index, 0)
        self.database_view.selectionModel().setCurrentIndex(
            qt_index, QItemSelectionModel.SelectionFlag.SelectCurrent)

        # if self.image_type == GuiImageType.FRAME:
        #     self.action_select_kymography_line.setEnabled(True)
        # else:
        #     self.action_select_kymography_line.setEnabled(False)

    def display_exclusion(self):
        """
        Updates title and graphs to show this Recording is excluded.
        """
        self.data_axes[0].set_title(
            self._get_title() + "\nNOTE: This recording has been excluded.")

    def next(self):
        """
        Callback function for the Next button.
        Increases cursor index, updates the view.
        """
        if self.index < self.max_index - 1:
            self._release_modality_memory()
            self.index += 1
            self._set_audio_for_player()
            self.update()
            self.update_ui()

    def prev(self):
        """
        Callback function for the Previous button.
        Decreases cursor index, updates the view.
        """
        if self.index > 0:
            self._release_modality_memory()
            self.index -= 1
            self._set_audio_for_player()
            self.update()
            self.update_ui()

    def go_to_recording(self, index: int):
        """
        Move to recording at index.

        Parameters
        ----------
        index : int
            Index of recording to move to.
        """
        self._release_modality_memory()
        self.index = index
        self._set_audio_for_player()
        self.update()
        self.update_ui()

    def go_to_callback(self):
        """
        Go to a recording specified in the goLineEdit text input field.
        """
        index_to_jump_to = int(self.go_to_line_edit.text()) - 1

        if 0 <= index_to_jump_to < len(self.session):
            self.go_to_recording(index=index_to_jump_to)

    def _update_pd_onset(self):
        audio = self.current.modalities['MonoAudio']
        if audio.go_signal is None:
            stimulus_onset = 0
        else:
            stimulus_onset = audio.go_signal

        # TODO 0.24: This should not be hard coded
        if 'PD l1 on RawUltrasound' in self.current.modalities:
            pd_metrics = self.current.modalities['PD l1 on RawUltrasound']
            ultra_time = pd_metrics.timevector - stimulus_onset
            index = self.current.annotations['frame_selection_index']
            self.current.annotations['selected_time'] = ultra_time[index]

    def next_frame(self):
        """
        Move the data cursor to the next frame.
        """
        # TODO 0.24: Remove hard coding again
        if 'PD l1 on RawUltrasound' not in self.current.modalities:
            return

        frame_selection_index = self.current.annotations[
            'frame_selection_index']
        pd = self.current.modalities['PD l1 on RawUltrasound']
        data_length = pd.data.size
        if -1 < frame_selection_index < data_length:
            self.current.annotations['frame_selection_index'] += 1
            _logger.debug(
                "next frame: %d",
                (self.current.annotations['frame_selection_index']))
            self._update_pd_onset()
            self.update()
            self.update_ui()

    def previous_frame(self):
        """
        Move the data cursor to the previous frame.
        """
        if self.current.annotations['frame_selection_index'] > 0:
            self.current.annotations['frame_selection_index'] -= 1
            _logger.debug(
                "previous frame: %d",
                (self.current.annotations['frame_selection_index']))
            self._update_pd_onset()
            self.update()
            self.update_ui()

    def rewind(self) -> None:
        """
        Move the selection cursor to beginning of the recording.
        """
        self.audio_player.stop()
        if self.current.annotations['selected_time'] > -1:
            new_cursor = self.current['MonoAudio'].modality_data.timevector[0]
            self.current.annotations['selected_time'] = new_cursor
        self.update()

    def image_updater(self) -> None:
        """
        Update which kind of image is shown in the small figure panel.
        """
        match self.menu_select_small_action_group.checkedAction():
            case self.action_mean_image:
                self.image_type = GuiImageType.MEAN_IMAGE
            case self.action_frame:
                self.image_type = GuiImageType.FRAME
            case self.action_raw_frame:
                self.image_type = GuiImageType.RAW_FRAME
            case _:
                _logger.warning("Somehow the small image type has been unset.")
        self.update()
        self.update_ui()

    def quit(self):
        """
        Quit the app.
        """
        self.audio_player.clear_audio()
        QCoreApplication.quit()

    def open(self):
        """
        Open either patkit saved data or import new data.
        """
        directory_name = QFileDialog.getExistingDirectory(
            self, caption="Open directory", directory='.'
        )
        if not directory_name:
            return  # User cancelled the dialog

        target_path = Path(directory_name)

        # TODO 0.24: this should be made into a proper option, now it's just
        # set at in run_annotator below
        # self.display_tongue = display_tongue

        path_type, target_path = resolve_open_path(target_path)

        match path_type:
            case OpenPathType.MANIFEST:
                scenarios = get_manifest_scenarios(path=target_path)
                if not scenarios:
                    raise ValueError("Manifest file is empty or invalid.")
                elif len(scenarios) == 1:
                    target_path = scenarios[0]
                else:
                    # Prompt the user to choose if multiple exist
                    scenario_strings = [str(p) for p in scenarios]
                    chosen_string, ok_pressed = ListSelectionDialog.get_item(
                        parent=self,
                        title="Select Scenario",
                        label="Multiple scenarios found. Select one:",
                        items=scenario_strings,
                        current=0,
                    )
                    if ok_pressed and chosen_string:
                        target_path = Path(chosen_string)
                    else:
                        return  # User cancelled the prompt
            case OpenPathType.SCENARIO:
                pass
            case OpenPathType.DIRECTORY:
                raise NotImplementedError(
                    "Opening a directory of data without "
                    "config is not implemented yet."
                )
            case OpenPathType.SINGLE_DATA:
                raise NotImplementedError(
                    "Opening a single data file without "
                    "config is not implemented yet."
                )
            case _:
                raise NotImplementedError(
                    f"Unknown path type {path_type}."
                )

        # Read config and data
        config, logger = initialise_config(
            path=target_path, require_gui=True
        )
        self.session = initialise_patkit(config=config, logger=logger)

        # Re-bind Configuration Properties
        self.config = config  # Update the annotator's config reference
        self.data_config = config.data_config
        self.gui_config = config.gui_config
        self.gui_mode = self.gui_config.color_scheme
        self._update_color_mode()

        # Reset Core State Variables
        self.recordings = self.session.recordings
        self.index = 0
        self.max_index = len(self.recordings)
        self.patgrid = self.current.patgrid  # self.current uses self.index

        # Update Validators and Database View
        go_validator = QIntValidator(1, self.max_index + 1, self)
        self.go_to_line_edit.setValidator(go_validator)
        self.replace_items_in_database_view(session=self.session)
        self._add_annotations()

        self.update()
        # In case labels change as new plots are drawn.
        self.figure.align_ylabels()
        self.update_ui()

    def open_file(self):
        """
        Open either patkit saved data or import new data.
        """
        filename = QFileDialog.getOpenFileName(
            self, caption="Open file", directory='.',
            filter="patkit files (*.patkit_meta)")
        _logger.warning(
            "Don't yet know how to open a file "
            "even though I know the name is %s.", filename)

    def save_all(self):
        """
        Save derived modalities and annotations.
        """
        # TODO 0.22.2: does this save textgrids too and how does it interact
        # with saving answers and exercises.
        save_recording_session(self.session)

    def save_textgrid(self):
        """
        Save the current TextGrid.
        """
        # TODO 0.22.2: write a call back for asking for overwrite confirmation.
        if self.mode is AnnotatorMode.EXERCISE:
            return

        if not self.current.textgrid_path:
            (self.current.textgrid_path, _) = QFileDialog.getSaveFileName(
                self, 'Save TextGrid', directory='.',
                filter="TextGrid files (*.TextGrid)")
        if self.current.textgrid_path and self.current.patgrid:
            file = self.current.textgrid_path
            with open(file, 'w', encoding='utf-8') as outfile:
                outfile.write(self.current.patgrid.format_long())
            _logger.info(
                "Wrote TextGrid to file %s.",
                str(self.current.textgrid_path))

    def save_all_textgrids(self):
        """
        Save the all TextGrids in this Session.
        """
        # TODO 0.22.2: write a call back for asking for overwrite confirmation.
        if self.mode is AnnotatorMode.EXERCISE:
            return

        for recording in self.session:
            if not recording.textgrid_path:
                # TODO: This will be SUPER ANNOYING when there are a lot of
                # recordings. Instead, ask for the directory to save in. In any
                # case needs to be reworked when patkit files no longer live
                # with the recorded data.
                (recording.textgrid_path, _) = QFileDialog.getSaveFileName(
                    self, 'Save TextGrid', directory='.',
                    filter="TextGrid files (*.TextGrid)")
            if recording.textgrid_path and recording.patgrid:
                file = recording.textgrid_path
                with open(file, 'w', encoding='utf-8') as outfile:
                    outfile.write(recording.patgrid.format_long())
                _logger.info(
                    "Wrote TextGrid to file %s.",
                    str(recording.textgrid_path))

    def create_exercise(self):
        """
        Wrap a directory as an Exercise.
        """
        # TODO: AFTER 1.0
        # ask for directory
        # ask for patkit/exercise dir
        # write patkit_v.yaml in exercise dir
        # mess up the textgrids as equidistant
        # show scrambled textgrid instead of original

    def open_exercise(self):
        # (exercise_config_path, _) = QFileDialog.getOpenFileName(
        #     self, 'Open Exercise', directory='.',
        #     filter="Exercise files (patkit_exercise.yaml)")
        # self.exercise = load_exercise(exercise_config_path)
        pass

    def open_answer(self):
        pass

    def save_answer(self):
        pass

    def compare_to_example(self):
        print("Comparing to model has not yet been implemented.")

    def show_example(self):
        """
        On 'Show example' menu item being triggered, update mode.
        """
        if self.action_show_example.isChecked():
            self.exercise_drop_down.setCurrentText(ExerciseMode.EXAMPLE.value)
        else:
            self.exercise_drop_down.setCurrentText(ExerciseMode.ANSWER.value)

    def to_annotator_mode(self) -> None:
        """
        Set the GUI to regular annotator mode.
        """
        self.menu_exercise.setEnabled(False)
        self.exercise_drop_down.setEnabled(False)
        self.action_save_all_textgrids.setEnabled(True)
        self.action_save_current_textgrid.setEnabled(True)
        self.plot_controller.to_annotator_mode(self.gui_mode)

        self.update()
        self.update_ui()

    def to_exercise_mode(self) -> None:
        """
        Set the GUI to exercise mode.
        """
        self.menu_exercise.setEnabled(True)
        self.exercise_drop_down.setEnabled(True)
        if self.exercise is None:
            self.exercise = Exercise(
                scenario=self.session,
            )
            self.exercise.new_blank_answer(cursor=self.cursor)
        self.action_save_all_textgrids.setEnabled(False)
        self.action_save_current_textgrid.setEnabled(False)
        self.plot_controller.to_exercise_mode(self.gui_mode)

        self.update()
        self.update_ui()

    def to_example_mode(self) -> None:
        """
        Set the GUI to showing example answer mode.
        """
        if not self.action_show_example.isChecked():
            self.action_show_example.setChecked(True)
        self.plot_controller.to_example_mode(self.gui_mode)

        self.update()
        self.update_ui()

    def to_answer_mode(self) -> None:
        """
        Set the GUI to answering exercise mode.
        """
        if self.action_show_example.isChecked():
            self.action_show_example.setChecked(False)
        self.plot_controller.to_answer_mode(self.gui_mode)

        self.update()
        self.update_ui()

    def mode_selection_changed(self, mode: str) -> None:
        """
        Callback for changing annotator mode.

        Parameters
        ----------
        mode : str
            The mode's name as a string.

        Raises
        ------
        ValueError
            If encountering an unimplemented mode an Error will be raised.
        """
        self.mode = AnnotatorMode(mode)
        match self.mode:
            case AnnotatorMode.ANALYSE:
                self.to_annotator_mode()
            case AnnotatorMode.EXERCISE:
                self.to_exercise_mode()
            case _:
                raise ValueError(f"Unknown Annotator Mode requested: {mode}.")

    def exercise_selection_changed(self, mode: str) -> None:
        """
        Callback for changing exercise mode.

        Parameters
        ----------
        mode : str
            The mode's name as a string.

        Raises
        ------
        ValueError
            If encountering an unimplemented mode an Error will be raised.
        """
        self.exercise_mode = ExerciseMode(mode)
        match self.exercise_mode:
            case ExerciseMode.EXAMPLE:
                self.to_example_mode()
            case ExerciseMode.ANSWER:
                self.to_answer_mode()
            case _:
                raise ValueError(f"Unknown Exercise Mode requested: {mode}.")

    def export_figure(self):
        """
        Callback method to export the current figure in any supported format.

        Opens a filedialog to ask for the filename. Save format is determined
        by file extension.
        """
        suggested_path = Path.cwd() / "patkit_figure.png"
        filename, _ = ImageSaveDialog.get_selection(
            name="Export the main figure",
            save_path=suggested_path,
            parent=self,
        )
        if filename is not None:
            self.figure.savefig(filename, bbox_inches='tight', pad_inches=0.05)
            export_session_and_recording_meta(
                filename=filename,
                session=self.session,
                recording=self.current,
                description="main GUI figure"
            )

    def export_ultrasound_frame(self) -> None:
        """
        Export the currently selected ultrasound frame and its meta data.

        The metadata is written to a separate `.txt` file of the same name as
        the image file.
        """
        # TODO: Add a check that grays out the export ultrasound figure when
        # one isn't available.

        if self.current.annotations['frame_selection_index'] >= 0:
            suggested_path = Path.cwd() / "Raw_ultrasound_frame.png"
            path, options = ImageSaveDialog.get_selection(
                name="Export ultrasound frame",
                save_path=suggested_path,
                parent=self,
                options={'Export interpolated frame': True}
            )
            if path is None:
                return

            if options['Export interpolated frame']:
                ultrasound_modality = self.current['RawUltrasound']
                interpolation_params = ultrasound_modality.interpolation_params
            else:
                interpolation_params = None

            export_ultrasound_frame_and_meta(
                filepath=path,
                session=self.session,
                recording=self.current,
                selection_index=self.current.annotations[
                    'frame_selection_index'],
                selection_time=self.current.annotations['selected_time'],
                ultrasound=self.current['RawUltrasound'],
                interpolation_params=interpolation_params
            )

    def export_aggregate_image(self) -> None:
        """
        Export AggregateImages connected with the current recording.

        The metadata is written to a separate `.txt` file of the same name as
        the corresponding image file.
        """
        statistics_names = self.current.statistics.keys()
        choice_list = [
            name for name in statistics_names if 'AggregateImage' in name]
        image_list, path, export_interpolated = ListSaveDialog.get_selection(
            name="Export AggregateImages",
            item_names=choice_list,
            parent=self,
            option_label='Export interpolated image'
        )
        if image_list is None:
            return

        if export_interpolated:
            ultrasound = "RawUltrasound"
            ultrasound_modality = next(
                recording[ultrasound] for recording in self.session
                if ultrasound in recording
            )
            interpolation_params = ultrasound_modality.interpolation_params
        else:
            interpolation_params = None

        for image in image_list:
            export_aggregate_image_and_meta(
                image=self.current.statistics[image],
                session=self.session,
                recording=self.current,
                path=path,
                interpolation_params=interpolation_params,
            )

    def export_distance_matrix(self) -> None:
        """
        Export DistanceMatrices connected with the current session.

        The metadata is written to a separate `.txt` file of the same name as
        the corresponding image file.
        """
        statistics_names = self.session.statistics.keys()
        choice_list = [
            name for name in statistics_names if 'DistanceMatrix' in name]
        matrix_list, path, _ = ListSaveDialog.get_selection(
            name="Export DistanceMatrices",
            item_names=choice_list,
            parent=self,
        )
        if matrix_list is None:
            return

        for matrix in matrix_list:
            export_distance_matrix_and_meta(
                matrix=self.session.statistics[matrix],
                session=self.session,
                path=path)

    def export_annotations_and_metadata(self) -> None:
        """
        Export annotations and some other meta data.
        """
        (filename, _) = QFileDialog.getSaveFileName(
            self, 'Save file', directory='.', filter="CSV files (*.csv)")

        if not filename:
            return

        vowels = ['a', 'A', 'e', 'E', 'i', 'I',
                  'o', 'O', 'u', '@', "@`", 'OI', 'V']
        fieldnames = ['basename', 'date_and_time', 'prompt', 'C1', 'C1_dur',
                      'word_dur', 'first_sound',
                      'first_sound_type', 'first_sound_dur', 'AAI']
        fieldnames.extend(self.default_annotations.keys())
        csv.register_dialect('tabseparated', delimiter='\t',
                             quoting=csv.QUOTE_NONE)

        with closing(open(filename, 'w', encoding='utf-8')) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore',
                                    dialect='tabseparated')

            writer.writeheader()
            for recording in self.recordings:
                annotations = recording.annotations.copy()
                annotations['basename'] = recording.basename
                annotations['date_and_time'] = (
                    recording.metadata.time_of_recording)
                annotations['prompt'] = recording.metadata.prompt
                annotations['word'] = recording.metadata.prompt.split()[0]

                word_dur = -1.0
                acoustic_onset = -1.0
                if 'word' in recording.textgrid:
                    for interval in recording.textgrid['word']:
                        # change this to access the phonemeDict and
                        # check for included words, then search for
                        # phonemes based on the same
                        if interval.text == "":
                            continue

                        # Before 1.0: check if there is a duration to use here.
                        # and maybe make this more intelligent by selecting
                        # purposefully the last non-empty first and taking the
                        # duration?
                        word_dur = interval.dur
                        stimulus_onset = (
                            recording['MonoAudio'].go_signal)
                        acoustic_onset = interval.xmin - stimulus_onset
                        break
                    annotations['word_dur'] = word_dur
                else:
                    annotations['word_dur'] = -1.0

                if acoustic_onset < 0 or annotations['selected_time'] < 0:
                    aai = -1.0
                else:
                    aai = acoustic_onset - annotations['selected_time']
                annotations['AAI'] = aai

                first_sound_dur = -1.0
                first_sound = ""
                if 'segment' in recording.textgrid:
                    for interval in recording.textgrid['segment']:
                        if interval.text and interval.text != 'beep':
                            first_sound_dur = interval.dur
                            first_sound = interval.text
                            break
                annotations['first_sound_dur'] = first_sound_dur
                annotations['first_sound'] = first_sound
                if first_sound in vowels:
                    annotations['first_sound_type'] = 'V'
                else:
                    annotations['first_sound_type'] = 'C'

                annotations['C1'] = recording.metadata.prompt[0]
                writer.writerow(annotations)
            _logger.info(
                "Wrote onset data in file %s.", filename)

    def point_added_cb(self, position: tuple[float, float], klass: str):
        """
        Callback for point being added to kymography line.

        Parameters
        ----------
        position : tuple[float, float]
            position of the point
        klass : str
            class name
        """
        x, y = position
        print(f"New point of class {klass} added at {x=}, {y=}.")

    def point_removed_cb(self, position: tuple[float, float], klass: str, idx):
        """
        Callback for point being removed from kymography line.

        Parameters
        ----------
        position : tuple[float, float]
            position of the point
        klass : str
            class name
        idx : _type_
            index of the point
        """
        x, y = position

        suffix = {"1": "st", "2": "nd", "3": "rd"}.get(str(idx)[-1], "th")
        print(
            f"The {idx}{suffix} point of class {klass} with "
            f"position {x=:.2f}, {y=:.2f}  was removed."
        )

    def pd_category_cb(self):
        """
        Callback function for the RadioButton for categorising
        the PD curve.
        """
        radio_button = self.sender()
        if radio_button.isChecked():
            self.current.annotations['pdCategory'] = radio_button.text()

    def tongue_position_cb(self):
        """
        Callback function for the RadioButton for categorising
        the PD curve.
        """
        radio_button = self.sender()
        if radio_button.isChecked():
            self.current.annotations['tonguePosition'] = radio_button.text()

    def on_database_view_clicked(self, index: QModelIndex):
        """
        Callback for handling clicks in the data base list view.

        Parameters
        ----------
        index : QModelIndex
            Index of the clicked item.
        """
        self.go_to_recording(index.row())

    def onpick(self, event):
        """
        Callback for handling time selection on events.
        """
        # TODO 0.23: swap None for -1 here and fix everything that breaks. this
        # will include zooming. probably a good idea to change the dict here
        # into a dataclass as well.
        if not event.xdata:
            self.current.annotations['selected_time'] = -1
            self.current.annotations['selection_index'] = -1
            self.current.annotations['frame_selection_index'] = -1
            self.current.annotations['selected_frequency'] = -1
            self.update()
            return

        subplot = 0
        for i, axes in enumerate(self.data_axes):
            if axes == event.inaxes:
                subplot = i + 1
                break

        _logger.debug(
            "Inside onpick - subplot: %d, x=%f, y=%f",
            subplot, event.xdata, event.ydata)

        audio = self.current.modalities['MonoAudio']
        if audio.go_signal is None:
            stimulus_onset = 0
        else:
            stimulus_onset = audio.go_signal

        # TODO 0.24: Remove hardcoding of modality names?
        if 'RawUltrasound' in self.current.modalities:
            timevector = (
                self.current.modalities['RawUltrasound'].timevector)
            distances = np.abs(timevector - stimulus_onset - event.xdata)
            self.current.annotations['frame_selection_index'] = np.argmin(
                distances)
            self.current.annotations['selected_time'] = event.xdata
        if 'MonoAudio' in self.current.modalities:
            timevector = (
                self.current.modalities['MonoAudio'].timevector)
            distances = np.abs(timevector - stimulus_onset - event.xdata)
            self.current.annotations['selection_index'] = np.argmin(distances)
            self.current.annotations['selected_time'] = event.xdata

        subplot_names = list(self.gui_config.data_axes.keys())
        if subplot-1 < len(subplot_names):
            if "spectrogram" in subplot_names[subplot-1]:
                self.current.annotations['selected_frequency'] = event.ydata
        else:
            self.current.annotations['selected_frequency'] = -1

        _logger.debug(
            "Inside onpick - subplot: %d, ultra_index=%d, audio_index=%d, x=%f",
            subplot,
            self.current.annotations['frame_selection_index'],
            self.current.annotations['selection_index'],
            self.current.annotations['selected_time'])

        self.update()

    def resize_event(self, event):
        """
        Window resize callback.
        """
        self.update()
        QMainWindow.resizeEvent(self, event)

    # noinspection PyPep8Naming
    def keyPressEvent(self, event):
        """
        Key press callback.

        QtPy is silly and wants the callback to have this specific name.
        """
        if event.key() == Qt.Key.Key_Shift:
            self.shift_is_held = True
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_is_held = True
        if event.key() == Qt.Key.Key_Alt:
            self.alt_is_held = True
        if event.key() == Qt.Key.Key_AltGr:
            self.alt_gr_is_held = True

        if self.alt_is_held or self.alt_gr_is_held:
            if event.key() == Qt.Key.Key_I:
                self.zoom_in()
            elif event.key() == Qt.Key.Key_O:
                self.zoom_out()
            elif event.key() == Qt.Key.Key_A:
                self.gui_config.auto_xlim = True
                self.gui_config.xlim = None
                self.update()
            elif event.key() == Qt.Key.Key_C:
                self.center_on_cursor()
            elif event.key() == Qt.Key.Key_Left:
                self.pan(left=True)
            elif event.key() == Qt.Key.Key_Right:
                self.pan(left=False)

    # noinspection PyPep8Naming
    def keyReleaseEvent(self, event):
        """
        Key release callback.

        QtPy is silly and wants the callback to have this specific name.
        """
        if event.key() == Qt.Key.Key_Shift:
            self.shift_is_held = False
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_is_held = False
        if event.key() == Qt.Key.Key_Alt:
            self.alt_is_held = False
        if event.key() == Qt.Key.Key_AltGr:
            self.alt_gr_is_held = False

    def on_color_scheme_changed(self, scheme: Qt.ColorScheme):
        """
        Call back to change from light to dark/vice versa with the system.
        """
        if scheme == Qt.ColorScheme.Light:
            self.change_to_light()
        else:
            self.change_to_dark()

    def zoom_in(self) -> None:
        """
        Zoom in to half the current viewed length in time.

        Will center on current cursor if there is a selection, otherwise will
        center on the current view.
        """
        self.gui_config.auto_xlim = False
        if self.current.annotations['selection_index'] >= 0:
            center = self.current.annotations['selected_time']
        elif self.current.annotations['frame_selection_index'] >= 0:
            center = self.current.annotations['selected_time']
        else:
            center = (self.xlim[0] + self.xlim[1]) / 2.0
        length = (self.xlim[1] - self.xlim[0]) * .25
        self.xlim = (center - length, center + length)
        if self.gui_config.xlim is not None:
            self.gui_config.xlim = self.xlim
        self.update()

    def zoom_out(self) -> None:
        """
        Zoom out to twice the current viewed length in time.

        Will center on current cursor if there is a selection, otherwise will
        center on the current view.
        """
        self.gui_config.auto_xlim = False
        center = (self.xlim[0] + self.xlim[1]) / 2.0
        length = self.xlim[1] - self.xlim[0]
        self.xlim = (center - length, center + length)
        if self.gui_config.xlim is not None:
            self.gui_config.xlim = self.xlim
        self.update()

    def pan(self, left: bool) -> None:
        """
        Pan left or right as instructed.

        Parameters
        ----------
        left : bool
            Pan left if True, right if False.
        """
        self.gui_config.auto_xlim = False
        quarter_length = (self.xlim[1] - self.xlim[0])/4
        if left:
            self.xlim = (
                self.xlim[0] - quarter_length,
                self.xlim[1] - quarter_length
            )
        else:
            self.xlim = (
                self.xlim[0] + quarter_length,
                self.xlim[1] + quarter_length
            )

        if self.gui_config.xlim is not None:
            self.gui_config.xlim = self.xlim
        self.update()

    def center_on_cursor(self) -> None:
        """
        Center main graph on selection cursor at the current zoom level.
        """
        self.gui_config.auto_xlim = False
        center = self.current.annotations['selected_time']
        half_length = (self.xlim[1] - self.xlim[0]) / 2.0
        self.xlim = (center - half_length, center + half_length)
        if self.gui_config.xlim is not None:
            self.gui_config.xlim = self.xlim
        self.update()

    @property
    def no_modifiers(self) -> bool:
        """
        True if no modifier keys are currently held down.

        Returns
        -------
        bool
            True if no modifier keys are currently held down.
        """
        modifiers_pressed = (
            self.shift_is_held or
            self.ctrl_is_held or
            self.alt_is_held or
            self.alt_gr_is_held
        )
        return not modifiers_pressed


def run_annotator(
        session: Session,
        config: Configuration,
) -> None:
    """
    Start the Annotator GUI.

    Parameters
    ----------
    session : Session
        The Session to run the Annotator on.
    config : config.Configuration
        Configuration mainly for the GUI, but passing the complete
        Configuration, because other things are occasionally needed.
    """
    app = QtWidgets.QApplication(sys.argv)
    # Apparently the assignment to an unused variable is needed
    # to avoid a segfault.
    app.annotator = PdQtAnnotator(
        session=session,
        display_tongue=True,
        config=config)
    QCoreApplication.setApplicationName("PATKIT")
    sys.exit(app.exec())
