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
"""Audio playback management and tracking."""

import time

import numpy as np
import sounddevice
from PyQt6 import QtCore


class AudioPlayer(QtCore.QObject):
    """
    Manages audio playback and broadcasts playback position.

    This class holds the current audio data and uses a timer to emit
    the current playback position, allowing UI elements to track the
    audio smoothly.

    Parameters
    ----------
    parent : QtCore.QObject | None
        The parent Qt object.
    """

    position_changed = QtCore.pyqtSignal(float)
    """Emitted constantly during playback with the time in seconds."""

    playback_stopped = QtCore.pyqtSignal()
    """Emitted when playback is stopped entirely."""

    playback_paused = QtCore.pyqtSignal(float)
    """Emitted when paused, providing the exact paused time."""

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._update_position)

        self._audio_data: np.ndarray | None = None
        self._sampling_rate: int = 44100
        self._current_position: float = 0.0
        self._start_time: float | None = None
        self._start_offset: float = 0.0

    def set_audio(self, audio_data: np.ndarray, sampling_rate: int) -> None:
        """
        Load new audio data into the player and reset the cursor.

        Parameters
        ----------
        audio_data : np.ndarray
            The audio data array to play. Passed by reference.
        samplerate : int
            The sampling rate of the audio data.
        """
        self.stop()
        self.clear_audio()
        self._audio_data = audio_data
        self._sampling_rate = sampling_rate
        self._current_position = 0.0

    def clear_audio(self) -> None:
        """
        Drop the reference to the audio array to free up memory.
        """
        self.stop()
        self._audio_data = None

    @QtCore.pyqtSlot()
    def play(self) -> None:
        """Start or resume playing the loaded audio data."""
        if self._audio_data is None:
            return

        start_idx = int(self._current_position * self._sampling_rate)
        if start_idx >= len(self._audio_data):
            self._current_position = 0.0
            start_idx = 0

        sounddevice.play(self._audio_data[start_idx:], self._sampling_rate)
        self._start_time = time.time()
        self._start_offset = self._current_position
        self._timer.start()

    @QtCore.pyqtSlot()
    def pause(self) -> None:
        """Pause playback and save the current position."""
        sounddevice.stop()
        self._timer.stop()
        if self._start_time is not None:
            self._current_position = (
                time.time() - self._start_time
            ) + self._start_offset
        self._start_time = None
        self.playback_paused.emit(self._current_position)

    @QtCore.pyqtSlot()
    def stop(self) -> None:
        """Stop playing audio and reset the position tracker."""
        sounddevice.stop()
        self._timer.stop()
        self._start_time = None
        self._current_position = 0.0
        self.playback_stopped.emit()

    def _update_position(self) -> None:
        """Calculate the current playback time and emit it."""
        if self._start_time is not None:
            current = (time.time() - self._start_time) + self._start_offset
            self.position_changed.emit(current)
