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
This is the main window of the PATKIT annotator.
"""

from PyQt6 import QtCore, QtGui, QtWidgets

from patkit.constants import AnnotatorMode, ExerciseMode
from patkit.data_structures import Session

from .player_controls import PlayerControls


class UiMainWindow(object):
    def setupUi(self, main_window):
        # Main elements and sizing
        main_window.setObjectName("MainWindow")
        # main_window.resize(1087, 795)
        main_window.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mplwindow = QtWidgets.QWidget(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.mplwindow.sizePolicy().hasHeightForWidth())
        self.mplwindow.setSizePolicy(sizePolicy)
        self.mplwindow.setObjectName("mplwindow")
        self.mplWindowVerticalLayout = QtWidgets.QVBoxLayout(self.mplwindow)
        self.mplWindowVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mplWindowVerticalLayout.setObjectName("mplWindowVerticalLayout")

        # Side panel
        self.side_panel = QtWidgets.QFrame(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.side_panel.sizePolicy().hasHeightForWidth()
        )
        self.side_panel.setSizePolicy(sizePolicy)
        self.side_panel.setMinimumSize(QtCore.QSize(150, 0))
        # self.side_panel.setMaximumSize(QtCore.QSize(300, 16777215))
        self.side_panel.setObjectName("side_panel")
        self.side_panel_layout = QtWidgets.QVBoxLayout(self.side_panel)
        self.side_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.side_panel_layout.setObjectName("side_panel_layout")

        # Vertical splitter for side panel (to resize/collapse ultrasound)
        self.side_panel_splitter = QtWidgets.QSplitter(
            QtCore.Qt.Orientation.Vertical)
        self.side_panel_layout.addWidget(self.side_panel_splitter)

        # Top container for side panel
        self.side_panel_top_widget = QtWidgets.QWidget()
        self.side_panel_top_layout = QtWidgets.QVBoxLayout(
            self.side_panel_top_widget)
        self.side_panel_top_layout.setContentsMargins(0, 0, 0, 0)
        self.side_panel_splitter.addWidget(self.side_panel_top_widget)

        # Mode selection
        self.mode_controls = QtWidgets.QGroupBox(self.side_panel_top_widget)
        self.mode_controls.setMaximumSize(QtCore.QSize(16777215, 80))
        self.mode_controls.setObjectName("mode_box")
        self.mode_layout = QtWidgets.QHBoxLayout(self.mode_controls)
        self.mode_layout.setContentsMargins(0, 0, 0, 0)
        self.mode_layout.setObjectName("mode_layout")

        self.mode_drop_down = QtWidgets.QComboBox(self.mode_controls)
        self.mode_drop_down.addItems(list(AnnotatorMode.values()))
        self.mode_layout.addWidget(self.mode_drop_down)
        self.exercise_drop_down = QtWidgets.QComboBox(self.mode_controls)
        self.exercise_drop_down.addItems(list(ExerciseMode.values()))
        self.mode_layout.addWidget(self.exercise_drop_down)
        self.side_panel_top_layout.addWidget(self.mode_controls)

        # Navigation buttons and widgets
        self.go_to_group = QtWidgets.QGroupBox(self.side_panel_top_widget)
        self.go_to_group.setMaximumSize(QtCore.QSize(16777215, 80))
        self.go_to_group.setObjectName("groupBox")
        self.go_to_layout = QtWidgets.QHBoxLayout(self.go_to_group)
        self.go_to_layout.setContentsMargins(0, 0, 0, 0)
        self.go_to_layout.setObjectName("go_to_layout")

        self.go_to_line_edit = QtWidgets.QLineEdit(self.go_to_group)
        self.go_to_line_edit.setMaximumSize(QtCore.QSize(80, 16777215))
        self.go_to_line_edit.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.go_to_line_edit.setObjectName("go_to_line_edit")
        self.go_to_layout.addWidget(self.go_to_line_edit)
        self.goButton = QtWidgets.QPushButton(self.go_to_group)
        self.goButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.goButton.setObjectName("goButton")
        self.go_to_layout.addWidget(self.goButton)

        self.previous_button = QtWidgets.QPushButton(self.go_to_group)
        self.previous_button.setMaximumSize(QtCore.QSize(80, 16777215))
        self.previous_button.setObjectName("previous_button")
        self.go_to_layout.addWidget(self.previous_button)
        self.next_button = QtWidgets.QPushButton(self.go_to_group)
        self.next_button.setMaximumSize(QtCore.QSize(80, 16777215))
        self.next_button.setObjectName("next_button")
        self.go_to_layout.addWidget(self.next_button)
        self.side_panel_top_layout.addWidget(self.go_to_group)

        # List view
        self.database_view = QtWidgets.QListView(self.side_panel_top_widget)
        self.database_model = QtGui.QStandardItemModel()
        self.database_view.setModel(self.database_model)
        self.database_view.setObjectName("databaseView")
        self.side_panel_top_layout.addWidget(self.database_view)
        self.database_view.clicked[QtCore.QModelIndex].connect(
            main_window.on_database_view_clicked)

        self.play_controls = PlayerControls(self.side_panel_top_widget)
        self.side_panel_top_layout.addWidget(self.play_controls)

        # Ultrasound frame display
        self.ultrasoundFrame = QtWidgets.QWidget(self.side_panel_top_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ultrasoundFrame.sizePolicy().hasHeightForWidth()
        )
        self.ultrasoundFrame.setSizePolicy(sizePolicy)
        self.ultrasoundFrame.setMinimumSize(QtCore.QSize(150, 100))
        self.ultrasoundFrame.setObjectName("ultrasoundFrame")

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.ultrasoundFrame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.side_panel_top_layout.addWidget(self.ultrasoundFrame)

        # TODO 1.1: Consider bringing these back as a e.g. a mode option like
        # exercises. Or build a customisation example from them. They are
        # connected with a section in translation code further below and in
        # two places in qt_annotator.
        #
        # Annotation radio buttons
        # self.positionRB = QtWidgets.QGroupBox(self.side_panel)
        # self.positionRB.setObjectName("positionRB")
        # self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.positionRB)
        # self.verticalLayout_5.setObjectName("verticalLayout_5")
        # self.positionRB_1 = QtWidgets.QRadioButton(self.positionRB)
        # self.positionRB_1.setAutoFillBackground(False)
        # self.positionRB_1.setObjectName("positionRB_1")
        # self.tonguePositionRBs = QtWidgets.QButtonGroup(main_window)
        # self.tonguePositionRBs.setObjectName("tonguePositionRBs")
        # self.tonguePositionRBs.addButton(self.positionRB_1)
        # self.verticalLayout_5.addWidget(self.positionRB_1)
        # self.positionRB_2 = QtWidgets.QRadioButton(self.positionRB)
        # self.positionRB_2.setAutoFillBackground(False)
        # self.positionRB_2.setObjectName("positionRB_2")
        # self.tonguePositionRBs.addButton(self.positionRB_2)
        # self.verticalLayout_5.addWidget(self.positionRB_2)
        # self.positionRB_3 = QtWidgets.QRadioButton(self.positionRB)
        # self.positionRB_3.setAutoFillBackground(False)
        # self.positionRB_3.setObjectName("positionRB_3")
        # self.tonguePositionRBs.addButton(self.positionRB_3)
        # self.verticalLayout_5.addWidget(self.positionRB_3)
        # self.side_panel_layout.addWidget(self.positionRB)

        # Main horizontal splitter for resizable side panel vs plots
        self.main_splitter = QtWidgets.QSplitter(
            QtCore.Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(self.side_panel)
        self.main_splitter.addWidget(self.mplwindow)
        # Give the plot window stretching priority when
        # resizing the whole application
        self.main_splitter.setStretchFactor(1, 1)
        self.horizontalLayout.addWidget(self.main_splitter)

        main_window.setCentralWidget(self.central_widget)

        # Menu bar
        # self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar = main_window.menuBar()
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")

        # Menus
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_export = QtWidgets.QMenu(self.menubar)
        self.menu_export.setObjectName("menu_export")
        self.menu_exercise = QtWidgets.QMenu(self.menubar)
        self.menu_exercise.setObjectName("menu_exercise")
        self.menu_image = QtWidgets.QMenu(self.menubar)
        self.menu_image.setObjectName("menu_image")
        # self.menu_mode = QtWidgets.QMenu(self.menubar)
        # self.menu_mode.setObjectName("menu_mode")
        self.menu_navigation = QtWidgets.QMenu(self.menubar)
        self.menu_navigation.setObjectName("menu_navigation")
        self.menu_script = QtWidgets.QMenu(self.menubar)
        self.menu_script.setEnabled(False)
        self.menu_script.setObjectName("menu_script")
        # main_window.setMenuBar(self.menubar)

        # Statusbar
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        # Menu items

        # File menu
        self.actionNew = QtGui.QAction(main_window)
        self.actionNew.setObjectName("actionNew")
        self.action_open = QtGui.QAction(main_window)
        self.action_open.setObjectName("action_open")
        self.action_save_all = QtGui.QAction(main_window)
        self.action_save_all.setObjectName("action_save_all")
        self.actionSave_as = QtGui.QAction(main_window)
        self.actionSave_as.setObjectName("actionSave_as")
        self.action_save_all_textgrids = QtGui.QAction(main_window)
        self.action_save_all_textgrids.setObjectName(
            "action_save_all_textgrids")
        self.action_save_current_textgrid = QtGui.QAction(main_window)
        self.action_save_current_textgrid.setObjectName(
            "action_save_current_textgrid")
        self.action_quit = QtGui.QAction(main_window)
        self.action_quit.setObjectName("action_quit")

        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save_current_textgrid)
        self.menu_file.addAction(self.action_save_all_textgrids)
        self.menu_file.addAction(self.action_save_all)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_quit)

        # Exercise menu actions
        self.action_new_exercise = QtGui.QAction(main_window)
        self.action_new_exercise.setObjectName("action_new_exercise")
        self.action_save_exercise = QtGui.QAction(main_window)
        self.action_save_exercise.setObjectName("action_save_exercise")
        self.action_new_answer = QtGui.QAction(main_window)
        self.action_new_answer.setObjectName("action_new_answer")
        self.action_save_answer = QtGui.QAction(main_window)
        self.action_save_answer.setObjectName("action_save_answer")
        self.action_open_answer = QtGui.QAction(main_window)
        self.action_open_answer.setObjectName("action_open_answer")
        self.action_compare_to_example = QtGui.QAction(main_window)
        self.action_compare_to_example.setObjectName(
            "action_compare_to_example")
        self.action_show_example = QtGui.QAction(main_window)
        self.action_show_example.setObjectName("action_show_example")

        self.menu_exercise.addAction(self.action_new_exercise)
        self.menu_exercise.addAction(self.action_save_exercise)
        self.menu_exercise.addSeparator()
        self.menu_exercise.addAction(self.action_new_answer)
        self.menu_exercise.addAction(self.action_save_answer)
        self.menu_exercise.addAction(self.action_open_answer)
        self.menu_exercise.addSeparator()
        self.menu_exercise.addAction(self.action_compare_to_example)
        self.menu_exercise.addAction(self.action_show_example)

        # TODO: 0.22: Implement this?
        self.action_compare_to_example.setEnabled(False)

        self.action_show_example.setCheckable(True)
        self.action_show_example.setChecked(False)

        # Export menu actions
        self.action_export_analysis = QtGui.QAction(main_window)
        self.action_export_analysis.setEnabled(False)
        self.action_export_analysis.setObjectName("action_export_analysis")
        self.action_export_main_figure = QtGui.QAction(main_window)
        self.action_export_main_figure.setObjectName(
            "action_export_main_figure")
        self.action_export_ultrasound_frame = QtGui.QAction(
            main_window)
        self.action_export_ultrasound_frame.setObjectName(
            "action_export_ultrasound_frame"
        )
        self.action_export_annotations_and_metadata = QtGui.QAction(
            main_window)
        self.action_export_annotations_and_metadata.setObjectName(
            "action_export_annotations_and_metadata"
        )
        self.action_export_aggregate_images = QtGui.QAction(
            main_window)
        self.action_export_aggregate_images.setObjectName(
            "action_export_aggregate_images"
        )
        self.action_export_distance_matrices = QtGui.QAction(
            main_window)
        self.action_export_distance_matrices.setObjectName(
            "action_export_distance_matrices"
        )

        self.menu_export.addAction(self.action_export_aggregate_images)
        self.menu_export.addAction(self.action_export_annotations_and_metadata)
        self.menu_export.addAction(self.action_export_distance_matrices)
        self.menu_export.addAction(self.action_export_main_figure)
        self.menu_export.addAction(self.action_export_ultrasound_frame)

        # Image actions
        self.menu_select_image = self.menu_image.addMenu("Select image")

        self.action_mean_image = QtGui.QAction(
            text="Mean image", parent=self.menu_select_image)
        self.action_frame = QtGui.QAction(
            text="Frame at cursor", parent=self.menu_select_image)
        self.action_raw_frame = QtGui.QAction(
            text="Raw frame at cursor", parent=self.menu_select_image)

        self.action_mean_image.setCheckable(True)
        self.action_frame.setCheckable(True)
        self.action_raw_frame.setCheckable(True)
        self.action_frame.setChecked(True)

        self.menu_select_image.addAction(self.action_mean_image)
        self.menu_select_image.addAction(self.action_frame)
        self.menu_select_image.addAction(self.action_raw_frame)

        self.menu_select_small_action_group = QtGui.QActionGroup(
            self.menu_select_image)
        self.menu_select_small_action_group.addAction(self.action_mean_image)
        self.menu_select_small_action_group.addAction(self.action_frame)
        self.menu_select_small_action_group.addAction(self.action_raw_frame)

        # Mode menu actions
        # self.mode_group = QtGui.QActionGroup(main_window)
        # self.action_annotator_mode = QtGui.QAction(main_window)
        # self.action_annotator_mode.setObjectName(
        #     "action_annotator_mode"
        # )
        # self.action_annotator_mode.setCheckable(True)
        # self.action_exercise_mode = QtGui.QAction(main_window)
        # self.action_exercise_mode.setObjectName(
        #     "action_exercise_mode"
        # )
        # self.action_exercise_mode.setCheckable(True)
        # self.mode_group.addAction(self.action_annotator_mode)
        # self.mode_group.addAction(self.action_exercise_mode)
        # self.action_annotator_mode.setChecked(True)
        # self.menu_mode.addAction(self.action_annotator_mode)
        # self.menu_mode.addAction(self.action_exercise_mode)

        # Navigation menu actions
        self.action_next = QtGui.QAction(main_window)
        self.action_next.setObjectName("action_next")
        self.action_previous = QtGui.QAction(main_window)
        self.action_previous.setObjectName("action_previous")
        self.action_next_frame = QtGui.QAction(main_window)
        self.action_next_frame.setObjectName("action_next_frame")
        self.action_previous_frame = QtGui.QAction(main_window)
        self.action_previous_frame.setObjectName("action_previous_frame")

        self.menu_navigation.addAction(self.action_next)
        self.menu_navigation.addAction(self.action_previous)
        self.menu_navigation.addSeparator()
        self.menu_navigation.addAction(self.action_next_frame)
        self.menu_navigation.addAction(self.action_previous_frame)

        # Script menu actions
        self.actionShow_interpreter = QtGui.QAction(main_window)
        self.actionShow_interpreter.setObjectName("actionShow_interpreter")
        self.actionRun_file = QtGui.QAction(main_window)
        self.actionRun_file.setObjectName("actionRun_file")

        # self.menu_script.addAction(self.actionShow_interpreter)
        # self.menu_script.addAction(self.actionRun_file)

        # Menubar setup
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_exercise.menuAction())
        self.menubar.addAction(self.menu_export.menuAction())
        self.menubar.addAction(self.menu_image.menuAction())
        # self.menubar.addAction(self.menu_mode.menuAction())
        self.menubar.addAction(self.menu_navigation.menuAction())
        self.menubar.addAction(self.menu_script.menuAction())

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(
            _translate("MainWindow", "PATKIT Annotator"))
        self.mode_controls.setTitle(_translate("MainWindow", "Annotator Mode"))
        self.go_to_group.setTitle(_translate("MainWindow", "Go to Recording"))
        self.goButton.setText(_translate("MainWindow", "Go"))
        self.previous_button.setText(_translate("MainWindow", "Previous"))
        self.next_button.setText(_translate("MainWindow", "Next"))

        # Annotation radio buttons
        # self.positionRB.setTitle(
        #     _translate("MainWindow", "Customised Metadata: TonguePosition")
        # )
        # self.positionRB_1.setText(_translate("MainWindow", "High"))
        # self.positionRB_2.setText(_translate("MainWindow", "Low"))
        # self.positionRB_3.setText(
        #     _translate("MainWindow", "Other / Not visible"))

        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.menu_exercise.setTitle(_translate("MainWindow", "Exercise"))
        self.menu_export.setTitle(_translate("MainWindow", "Export"))
        self.menu_image.setTitle(_translate("MainWindow", "Image"))
        # self.menu_mode.setTitle(_translate("MainWindow", "Mode"))
        self.menu_navigation.setTitle(_translate("MainWindow", "Navigation"))
        self.menu_script.setTitle(_translate("MainWindow", "Script"))

        self.action_new_exercise.setText(
            _translate("MainWindow", "New exercise..."))
        self.action_save_exercise.setText(
            _translate("MainWindow", "Save exercise"))
        self.action_new_answer.setText(
            _translate("MainWindow", "New answer..."))
        self.action_save_answer.setText(
            _translate("MainWindow", "Save answer"))
        self.action_open_answer.setText(
            _translate("MainWindow", "Open answer..."))
        self.action_compare_to_example.setText(
            _translate("MainWindow", "Compare to example"))
        self.action_show_example.setText(
            _translate("MainWindow", "Show example"))
        self.action_show_example.setShortcut(
            _translate("MainWindow", "Alt+E"))

        self.actionNew.setText(_translate("MainWindow", "New"))
        self.action_open.setText(_translate("MainWindow", "Open..."))
        self.action_open.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.action_save_all.setText(_translate("MainWindow", "Save all"))
        self.action_save_all.setShortcut(
            _translate("MainWindow", "Ctrl+Shift+S"))
        self.actionShow_interpreter.setText(
            _translate("MainWindow", "Show interpreter")
        )
        self.actionRun_file.setText(_translate("MainWindow", "Run file..."))
        self.action_next.setText(_translate("MainWindow", "Next Recording"))
        self.action_next.setShortcut(_translate("MainWindow", "Down"))
        self.action_previous.setText(
            _translate("MainWindow", "Previous Recording"))
        self.action_previous.setShortcut(_translate("MainWindow", "Up"))
        self.action_export_analysis.setText(
            _translate("MainWindow", "Export analysis...")
        )
        self.action_next_frame.setText(_translate("MainWindow", "Next Frame"))
        self.action_next_frame.setShortcut(_translate("MainWindow", "Right"))
        self.action_previous_frame.setText(
            _translate("MainWindow", "Previous Frame"))
        self.action_previous_frame.setShortcut(
            _translate("MainWindow", "Left"))
        self.action_export_main_figure.setText(
            _translate("MainWindow", "Export main figure...")
        )
        self.action_export_main_figure.setShortcut(
            _translate("MainWindow", "Ctrl+E"))
        self.action_export_ultrasound_frame.setText(
            _translate("MainWindow", "Export ultrasound figure...")
        )
        self.action_export_annotations_and_metadata.setText(
            _translate("MainWindow", "Export annotations and metadata...")
        )
        self.action_export_aggregate_images.setText(
            _translate("MainWindow", "Export aggregate images...")
        )
        self.action_save_all_textgrids.setText(
            _translate("MainWindow", "Save all TextGrids")
        )
        self.action_save_current_textgrid.setText(
            _translate("MainWindow", "Save current TextGrid")
        )

        self.menu_select_image.setTitle(
            _translate("MainWindow", "Select image"))
        self.action_mean_image.setText(
            _translate("MainWindow", "Mean image"))
        self.action_frame.setText(
            _translate("MainWindow", "Frame at cursor"))
        self.action_raw_frame.setText(
            _translate("MainWindow", "Raw frame at cursor"))

        self.action_quit.setText(_translate("MainWindow", "Quit"))
        self.action_quit.setShortcut(_translate("MainWindow", "Ctrl+Q"))

        self.action_export_distance_matrices.setText(
            _translate("MainWindow", "Export distance matrices...")
        )

        # self.action_exercise_mode.setText(
        #   _translate("MainWindow", "Exercise"))
        # self.action_annotator_mode.setText(
        #     _translate("MainWindow", "Annotator"))

    def add_items_to_database_view(self, session: Session):
        """
        Add items/recordings to the list view.

        Parameters
        ----------
        session : Session
            Use the recordings in the given session to populate the list view.
        """
        for recording in session:
            self.database_model.appendRow(
                QtGui.QStandardItem(
                    f"{recording.basename}: "
                    f"{recording.metadata.prompt.strip()}"
                )
            )

    def replace_items_in_database_view(self, session: Session):
        """
        Replace the items/recordings in the list view.

        Parameters
        ----------
        session : Session
            Use the recordings in the given Session to replace the old ones.
        """
        self.database_model.clear()
        self.add_items_to_database_view(session)
