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
Dialogs for Exercises and Answers.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget
)

from patkit.constants import ExerciseScrambler


class NewExerciseDialog(QDialog):
    """Dialog for configuring a new Exercise."""

    def __init__(
        self,
        parent: QWidget | None = None,
        path: Path | None = None
    ):
        super().__init__(parent)

        if path is None:
            self.base_dir = Path.cwd()
        else:
            self.base_dir = path / 'exercise_name'

        self.setWindowTitle("New Exercise")

        self.scrambling_method = "equidistant"

        method_box = QHBoxLayout()
        self.method_label = QLabel("Scrambling Method:", self)
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(ExerciseScrambler.values())
        method_box.addWidget(self.method_label)
        method_box.addWidget(self.method_combo)

        # path_box = QHBoxLayout()
        # self.path_label = QLabel("Exercise Directory:", self)
        # self.path_field = QLineEdit(str(self.base_dir), self)
        # self.browse_button = QPushButton("Browse...")
        # self.browse_button.clicked.connect(self._browse)
        # path_box.addWidget(self.path_label)
        # path_box.addWidget(self.path_field)
        # path_box.addWidget(self.browse_button)

        dialog_buttons = (
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_cancel_buttons = QDialogButtonBox(dialog_buttons)
        self.ok_cancel_buttons.accepted.connect(self._on_accepted)
        self.ok_cancel_buttons.rejected.connect(self.reject)

        vbox = QVBoxLayout(self)
        vbox.addLayout(method_box)
        # vbox.addLayout(path_box)
        vbox.addWidget(self.ok_cancel_buttons)

        # self.path_field.setSizePolicy(
        #     QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(400)

    def _browse(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select Exercise Directory",
            directory=self.path_field.text(),
            options=QFileDialog.Option.DontResolveSymlinks
        )
        if directory:
            self.path_field.setText(directory)

    def _on_accepted(self) -> None:
        self.scrambling_method = self.method_combo.currentText()
        # self.base_dir = Path(self.path_field.text())
        self.accept()

    @staticmethod
    def get_exercise_params(
        parent: QWidget | None = None,
        path: Path | None = None,
    ) -> str | None:
        dialog = NewExerciseDialog(parent=parent, path=path)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return None
        return dialog.scrambling_method


class NewAnswerDialog(QDialog):
    """Dialog for configuring a new Answer."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("New Answer")

        self.author_name = ""
        self.answer_name = ""

        answer_box = QHBoxLayout()
        self.answer_label = QLabel("Answer Name:", self)
        self.answer_field = QLineEdit(self)
        answer_box.addWidget(self.answer_label)
        answer_box.addWidget(self.answer_field)

        author_box = QHBoxLayout()
        self.author_label = QLabel("Author Name (optional):", self)
        self.author_field = QLineEdit(self)
        author_box.addWidget(self.author_label)
        author_box.addWidget(self.author_field)

        dialog_buttons = (
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_cancel_buttons = QDialogButtonBox(dialog_buttons)
        self.ok_cancel_buttons.accepted.connect(self._on_accepted)
        self.ok_cancel_buttons.rejected.connect(self.reject)

        vbox = QVBoxLayout(self)
        vbox.addLayout(answer_box)
        vbox.addLayout(author_box)
        vbox.addWidget(self.ok_cancel_buttons)
        self.adjustSize()

    def _on_accepted(self) -> None:
        self.author_name = self.author_field.text()
        self.answer_name = self.answer_field.text()
        if not self.answer_name:
            self.reject()
        self.accept()

    @staticmethod
    def get_answer_params(
        parent: QWidget | None = None
    ) -> tuple[str | None, str | None]:
        """
        Open a dialog and query user for Answer name and author name.

        Parameters
        ----------
        parent : QWidget | None, optional
            Parent window.

        Returns
        -------
        tuple[str | None, str | None]
            Either the Answer name and optionally the author name, or a pair of
            Nones if the user cancelled.
        """
        dialog = NewAnswerDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return None, None
        return dialog.answer_name, dialog.author_name


class PackageExerciseDialog(QDialog):
    """
    Dialog for configuring an Exercise packaging.

    This dialog allows the user to specify a package path and choose whether
    to include the unscrambled Session TextGrids in the resulting archive.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        default_path: Path | None = None
    ) -> None:
        """
        Initialize the PackageExerciseDialog.

        Parameters
        ----------
        parent : QWidget | None, optional
            The parent widget, by default None.
        default_path : Path | None, optional
            The default file path to populate the dialog, by default None.
        """
        super().__init__(parent=parent)
        self.setWindowTitle("Package Exercise")
        self.resize(700, 100)

        self.package_path: Path | None = None
        self.include_textgrids: bool = False

        self.path_label = QLabel(text="Package Path:", parent=self)
        self.path_field = QLineEdit(parent=self)
        if default_path is not None:
            self.path_field.setText(str(default_path))

        self.browse_button = QPushButton(text="Browse...", parent=self)
        self.browse_button.clicked.connect(slot=self._browse)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_field)
        path_layout.addWidget(self.browse_button)

        self.textgrid_checkbox = QCheckBox(
            text=(
                "Include original TextGrids (this will make "
                "them viewable when running the exercise)."
            ),
            parent=self
        )

        dialog_buttons = (
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_cancel_buttons = QDialogButtonBox(dialog_buttons)
        self.ok_cancel_buttons.accepted.connect(slot=self._on_accepted)
        self.ok_cancel_buttons.rejected.connect(slot=self.reject)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.textgrid_checkbox)
        main_layout.addWidget(self.ok_cancel_buttons)

        self.setMinimumWidth(450)

    def _browse(self) -> None:
        """Open a file dialog to select the destination zip path."""
        file_path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Select Packaging Destination",
            directory=self.path_field.text(),
            filter="Zip Files (*.zip)"
        )
        if file_path:
            self.path_field.setText(file_path)

    def _on_accepted(self) -> None:
        """Validate input and accept the dialog."""
        path_text = self.path_field.text()
        if not path_text:
            self.reject()
            return

        self.package_path = Path(path_text)
        self.include_textgrids = self.textgrid_checkbox.isChecked()
        self.accept()

    @staticmethod
    def get_packaging_params(
        parent: QWidget | None = None,
        default_path: Path | None = None
    ) -> tuple[Path | None, bool]:
        """
        Open the package dialog and query the user for packaging parameters.

        Parameters
        ----------
        parent : QWidget | None, optional
            Parent window.
        default_path : Path | None, optional
            The default file path to populate the line edit.

        Returns
        -------
        tuple[Path | None, bool]
            The selected file path and boolean indicating if TextGrids
            should be included. Path is None if the user cancelled.
        """
        dialog = PackageExerciseDialog(
            parent=parent, default_path=default_path
        )
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return None, False

        return dialog.package_path, dialog.include_textgrids
