"""
Dialogs for Exercises and Answers.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget
)

from patkit.constants import ExerciseScrambler, PatkitDirectory


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

        path_box = QHBoxLayout()
        self.path_label = QLabel("Exercise Directory:", self)
        self.path_field = QLineEdit(str(self.base_dir), self)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse)
        path_box.addWidget(self.path_label)
        path_box.addWidget(self.path_field)
        path_box.addWidget(self.browse_button)

        dialog_buttons = (
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_cancel_buttons = QDialogButtonBox(dialog_buttons)
        self.ok_cancel_buttons.accepted.connect(self._on_accepted)
        self.ok_cancel_buttons.rejected.connect(self.reject)

        vbox = QVBoxLayout(self)
        vbox.addLayout(method_box)
        vbox.addLayout(path_box)
        vbox.addWidget(self.ok_cancel_buttons)

        self.path_field.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(600)

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
        self.base_dir = Path(self.path_field.text())
        self.accept()

    @staticmethod
    def get_exercise_params(
        parent: QWidget | None = None,
        path: Path | None = None,
    ) -> tuple[Path | None, str | None]:
        dialog = NewExerciseDialog(parent=parent, path=path)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return None, None
        return dialog.base_dir, dialog.scrambling_method


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
