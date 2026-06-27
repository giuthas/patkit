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
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QDialogButtonBox,
    QWidget
)


class ListSelectionDialog(QDialog):
    """
    A custom dialog that mimics QInputDialog.getItem but uses a QListWidget
    instead of a QComboBox for better readability of long strings (like paths).
    """

    def __init__(
        self,
        parent: QWidget | None,
        title: str,
        label: str,
        items: list[str],
        current: int = 0,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))

        self.list_widget = QListWidget()
        self.list_widget.addItems(items)

        # Set the default selected row if within bounds
        if 0 <= current < len(items):
            self.list_widget.setCurrentRow(current)

        # Allow double-clicking an item to act as clicking "OK"
        self.list_widget.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.list_widget)

        # Standard OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def get_item(
        parent: QWidget | None,
        title: str,
        label: str,
        items: list[str],
        current: int = 0,
        **kwargs
    ) -> tuple[str, bool]:
        """
        Static method that exactly mirrors QInputDialog.getItem signature.

        Returns
        -------
        tuple[str, bool]
            The selected string and a boolean indicating if OK was pressed.
        """
        dialog = ListSelectionDialog(
            parent=parent,
            title=title,
            label=label,
            items=items,
            current=current
        )

        # Execute the dialog blockingly
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            if dialog.list_widget.currentItem():
                return dialog.list_widget.currentItem().text(), True

        return "", False
