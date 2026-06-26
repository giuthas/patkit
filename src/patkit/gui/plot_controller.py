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
"""Matplotlib canvas and axes management for the GUI."""

import logging

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.widgets import MultiCursor
import numpy as np

from patkit.data_structures import Recording
from patkit.configuration import DataConfig, GuiConfig
from patkit.constants import (
    AnnotatorMode, DefaultCanvasColors, DefaultCursorColors,
    ExerciseMode, GuiColorScheme, GuiImageType
)
from patkit.plot_and_publish import (
    format_legend,
    get_colors_in_sequence,
    mark_peaks,
    plot_patgrid_tier,
    plot_spectrogram,
    plot_spectrogram2,
    plot_spline,
    plot_timeseries,
    plot_wav,
)

from .annotator_window import UiMainWindow
from .boundary_animation import BoundaryAnimator

_logger = logging.getLogger(__name__)


class PlotController:
    """
    Manages the Matplotlib figure, canvas, and tracking cursors.

    Encapsulates the Matplotlib setup required for rendering and provides
    utility methods for updating playback cursors across all axes. Handles both
    the main data/tier canvas and the secondary ultrasound canvas.
    """

    def __init__(
        self,
        data_config: DataConfig,
        gui_config: GuiConfig,
        main_window: UiMainWindow
    ) -> None:
        """

        Parameters
        ----------
        data_config : DataConfig
            The data configuration.
        gui_config : GuiConfig
            The GUI configuration.
        main_window : UiMainWindow
            The main window encapsulating the annotator.
        """
        self.main_window = main_window

        # Main Canvas Setup
        self.figure = Figure(layout="tight")
        self.canvas = FigureCanvas(self.figure)

        # Ultrasound Canvas Setup
        self.ultra_fig = Figure()
        self.ultra_canvas = FigureCanvas(self.ultra_fig)
        self.ultra_axes = self.ultra_fig.add_axes((0, 0, 1, 1))

        self.data_axes: list = []
        self.tier_axes: list = []

        # Cursor Tracking
        self.playback_cursor_lines: list[Line2D] = []
        self.selection_artists: list = []
        self.multicursor: MultiCursor | None = None
        self.playback_background = None

        # Original axes state caching for fast updates
        self.original_xticks = []
        self.original_yticks = {}

        self.main_grid_spec = None
        self.tier_grid_spec = None
        self.data_grid_spec = None

        self.data_config = data_config
        self.gui_config = gui_config
        self.set_style(self.gui_config)

    def set_style(self, gui_config: GuiConfig) -> None:
        """
        Set/reset gui configuration.

        Parameters
        ----------
        gui_config : GuiConfig
            The GUI configuration.
        """
        self.gui_config = gui_config
        matplotlib.rcParams.update(
            {'font.size': self.gui_config.default_font_size}
        )
        plt.style.use('tableau-colorblind10')

    def to_annotator_mode(
        self,
        gui_color_mode: GuiColorScheme = GuiColorScheme.LIGHT
    ) -> None:
        """
        Set the GUI to regular annotator mode.
        """
        match gui_color_mode:
            case GuiColorScheme.DARK:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.ANNOTATOR_DARK)
            case GuiColorScheme.LIGHT:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.ANNOTATOR_LIGHT)
            case _:
                raise ValueError(
                    f"Unknown GUI color scheme: {gui_color_mode}"
                )

    def to_exercise_mode(
        self,
        gui_color_mode: GuiColorScheme = GuiColorScheme.LIGHT
    ) -> None:
        """
        Set the GUI to exercise mode.
        """
        match gui_color_mode:
            case GuiColorScheme.DARK:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.ANSWER_DARK)
            case GuiColorScheme.LIGHT:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.ANSWER_LIGHT)
            case _:
                raise ValueError(
                    f"Unknown GUI color scheme: {gui_color_mode}"
                )

    def to_example_mode(
        self,
        gui_color_mode: GuiColorScheme = GuiColorScheme.LIGHT
    ) -> None:
        """
        Set the GUI to showing example answer mode.
        """
        match gui_color_mode:
            case GuiColorScheme.DARK:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.EXAMPLE_DARK)
            case GuiColorScheme.LIGHT:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.EXAMPLE_LIGHT)
            case _:
                raise ValueError(
                    f"Unknown GUI color scheme: {gui_color_mode}"
                )

    def to_answer_mode(
        self,
        gui_color_mode: GuiColorScheme = GuiColorScheme.LIGHT
    ) -> None:
        """
        Set the GUI to answering exercise mode.
        """
        match gui_color_mode:
            case GuiColorScheme.DARK:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.ANSWER_DARK)
            case GuiColorScheme.LIGHT:
                self.figure.patch.set_facecolor(
                    DefaultCanvasColors.ANSWER_LIGHT)
            case _:
                raise ValueError(
                    f"Unknown GUI color scheme: {gui_color_mode}"
                )

    def setup_axes(self) -> None:
        """
        Clear the figure and set up the required subplots.
        """
        self.figure.clear()
        self.data_axes = []
        self.tier_axes = []

        height_ratios = [
            self.gui_config.data_and_tier_height_ratios.data_axes,
            self.gui_config.data_and_tier_height_ratios.tier_axes
        ]
        self.main_grid_spec = self.figure.add_gridspec(
            nrows=2,
            ncols=1,
            hspace=0,
            wspace=0,
            height_ratios=height_ratios,
        )

        number_of_data_axes = self.gui_config.number_of_data_axes
        self.data_grid_spec = self.main_grid_spec[0].subgridspec(
            number_of_data_axes, 1, hspace=0, wspace=0)

        data_axes_params = None
        if self.gui_config.general_axes_params:
            if self.gui_config.general_axes_params is not None:
                data_axes_params = self.gui_config.general_axes_params

        for i, axes_name in enumerate(self.gui_config.data_axes):
            sharex = False
            if self.gui_config.data_axes[axes_name].sharex:
                sharex = self.gui_config.data_axes[axes_name].sharex
            elif (data_axes_params is not None and
                  data_axes_params.sharex is not None):
                sharex = data_axes_params.sharex

            if i != 0 and sharex:
                ax = self.figure.add_subplot(
                    self.data_grid_spec[i],
                    sharex=self.data_axes[0])
            else:
                ax = self.figure.add_subplot(
                    self.data_grid_spec[i])
            self.data_axes.append(ax)

        self.canvas.draw_idle()

    def clear_axes(self) -> None:
        """Clear all data axes."""
        for axes in self.data_axes + self.tier_axes:
            axes.cla()

    def draw_plots(
        self,
        recording: Recording,
        patgrid: list,
        xlim: tuple[float, float],
        mode: AnnotatorMode,
        exercise_mode: ExerciseMode,
        title: str,
    ) -> None:
        """
        Dynamically calculate grid specs and draw the data and tiers.
        """
        if recording.excluded:
            self.display_exclusion()

        self.setup_axes()

        if 'MonoAudio' in recording.modalities:
            self.data_axes[0].set_title(title)
        else:
            self.data_axes[0].set_title(
                title + "\nNOTE: Audio missing.")
            return

        for axes in self.tier_axes:
            axes.remove()
        self.tier_axes = []
        # if current_recording.patgrid:
        if patgrid:
            nro_tiers = len(patgrid)
            self.tier_grid_spec = self.main_grid_spec[1].subgridspec(
                nro_tiers, 1, hspace=0, wspace=0)
            for axes_counter, tier in enumerate(patgrid):
                axes = self.figure.add_subplot(
                    self.tier_grid_spec[axes_counter],
                    sharex=self.data_axes[0])
                axes.set_yticks([])
                self.tier_axes.append(axes)

        # Hide all bottom ticks for data axes initially
        for axes in self.data_axes:
            axes.xaxis.set_tick_params(bottom=False, labelbottom=False)
        self.data_axes[0].xaxis.set_tick_params(top=True, labeltop=True)

        # Hide bottom ticks for all tier axes EXCEPT the last one
        for axes in self.tier_axes[:-1]:
            axes.xaxis.set_tick_params(bottom=False, labelbottom=False)

        # Explicitly enforce ticks ON for the bottom-most axis so MultiCursor
        # doesn't flush them away during updates.
        if self.tier_axes:
            self.tier_axes[-1].xaxis.set_tick_params(
                bottom=True, labelbottom=True)
        elif self.data_axes:
            self.data_axes[-1].xaxis.set_tick_params(
                bottom=True, labelbottom=True)

        if 'MonoAudio' not in recording.modalities:
            return

        audio = recording.modalities['MonoAudio']
        if audio.go_signal is None:
            stimulus_onset = 0
        else:
            stimulus_onset = audio.go_signal

        wav = audio.data
        wav_time = audio.timevector - stimulus_onset

        if self.gui_config.xlim is not None:
            xlim = self.gui_config.xlim
        elif self.gui_config.auto_xlim:
            x_minimums = []
            x_maximums = []
            modalities_to_check = self.gui_config.plotted_modality_names()
            modalities_to_check.add("MonoAudio")
            for name in modalities_to_check:
                if name in recording:
                    x_minimums.append(
                        recording[name].timevector[0] - stimulus_onset
                    )
                    x_maximums.append(
                        recording[name].timevector[-1] - stimulus_onset
                    )
            xlim = (np.min(x_minimums)-.05, np.max(x_maximums)+.05)

        axes_counter = 0
        for axes_name in self.gui_config.data_axes:
            self.data_axes[axes_counter].grid(False)
            match axes_name:
                case "spectrogram":
                    if self.gui_config.data_axes[axes_name].ylim is not None:
                        ylim = self.gui_config.data_axes[axes_name].ylim
                    else:
                        ylim = (0, 10500)
                    plot_spectrogram(self.data_axes[axes_counter],
                                     waveform=wav,
                                     ylim=ylim,
                                     sampling_frequency=audio.sampling_rate,
                                     extent_on_x=(wav_time[0], wav_time[-1]))
                case "spectrogram2":
                    if self.gui_config.data_axes[axes_name].ylim is not None:
                        ylim = self.gui_config.data_axes[axes_name].ylim
                    else:
                        ylim = (0, 10500)
                    plot_spectrogram2(
                        self.data_axes[axes_counter],
                        waveform=wav,
                        ylim=ylim,
                        sampling_frequency=audio.sampling_rate,
                        extent_on_x=(wav_time[0], wav_time[-1]),
                        mode=self.gui_config.color_scheme
                    )
                case "wav":
                    plot_wav(
                        ax=self.data_axes[axes_counter],
                        waveform=wav,
                        wav_time=wav_time,
                        xlim=xlim,
                        mode=self.gui_config.color_scheme
                    )
                case _:
                    if not recording.excluded:
                        self.plot_modality_axes(
                            recording=recording,
                            xlim=xlim,
                            axes_number=axes_counter,
                            axes_name=axes_name,
                            zero_offset=stimulus_onset,
                            ylim=self.gui_config.data_axes[axes_name].ylim,
                        )
            axes_counter += 1

        self.animators = []
        iterator = zip(patgrid.items(),
                       self.tier_axes, strict=True)
        for (name, tier), axis in iterator:
            axis.grid(False)
            boundaries_by_axis = []

            boundary_set, _ = plot_patgrid_tier(
                axes=axis,
                tier=tier,
                time_offset=stimulus_onset,
                text_y=.5,
                xlim=xlim,
            )
            boundaries_by_axis.append(boundary_set)
            axis.set_ylabel(
                name, rotation=90, horizontalalignment="center",
                verticalalignment="center")
            axis.set_xlim(xlim)
            if name in self.gui_config.pervasive_tiers:
                for data_axis in self.data_axes:
                    boundary_set = plot_patgrid_tier(
                        axes=data_axis,
                        tier=tier,
                        time_offset=stimulus_onset,
                        draw_text=False)[0]
                    boundaries_by_axis.append(boundary_set)

            # Change rows to be individual boundaries instead of axis. This
            # makes it possible to create animators for each boundary as
            # represented by multiple lines on different axes.
            boundaries_by_boundary = list(map(list, zip(*boundaries_by_axis)))

            tier_limits = [
                xlim[0] + stimulus_onset, xlim[1] + stimulus_onset]
            tier_in_limits = tier.intersects(xlim=tier_limits)
            if (
                mode is AnnotatorMode.ANALYSE or
                exercise_mode is ExerciseMode.ANSWER
            ):
                for boundaries, interval in zip(
                        boundaries_by_boundary, tier_in_limits, strict=True):
                    animator = BoundaryAnimator(
                        main_window=self.main_window,
                        boundaries=boundaries,
                        segment=interval,
                        epsilon=self.data_config.epsilon,
                        time_offset=stimulus_onset)
                    animator.connect()
                    self.animators.append(animator)
        if self.tier_axes:
            self.tier_axes[-1].set_xlabel("Time (s)")

        # Save clean ticks to avoid infinite accumulation
        # when adding selection ticks
        self.original_xticks = self.data_axes[0].get_xticks()
        self.original_yticks = {ax: ax.get_yticks() for ax in self.data_axes}

        self.update_selection_cursors(recording)

        self.playback_cursor_lines = []
        for ax in self.data_axes + self.tier_axes:
            line = ax.axvline(
                x=0,
                color=DefaultCursorColors.PLAYBACK,
                linestyle='-',
                visible=False
            )
            self.playback_cursor_lines.append(line)

        # Restore MultiCursor
        self.update_multicursor()

        # Align the y-labels nicely across all subplots
        self.figure.align_ylabels()

    def update_selection_cursors(self, recording: Recording) -> None:
        """
        Update the selection cursors across the subplots.

        Fast path for rendering the selection cursors and tick
        modifications without a full canvas wipe/rebuild.
        """
        # Clean up old drawn selection lines
        for artist in getattr(self, 'selection_artists', []):
            try:
                artist.remove()
            except Exception:
                pass
        self.selection_artists = []

        # Reset ticks to their clean original states
        if hasattr(self, 'original_xticks') and len(self.original_xticks) > 0:
            self.data_axes[0].set_xticks(self.original_xticks)

            # Remove deepskyblue from regular ticks
            for label in self.data_axes[0].get_xticklabels():
                label.set_color("black")
            if self.tier_axes:
                for label in self.tier_axes[-1].get_xticklabels():
                    label.set_color("black")

        if hasattr(self, 'original_yticks'):
            for ax, yticks in self.original_yticks.items():
                ax.set_yticks(yticks)

        selected_time = recording.annotations['selected_time']
        selected_freq = recording.annotations['selected_frequency']

        # Apply the new selection
        if selected_time > -1:
            old_ticks = self.original_xticks
            if len(old_ticks) > 2:
                self.data_axes[0].set_xticks(
                    [old_ticks[1], selected_time, old_ticks[-2]]
                )
            elif len(old_ticks) > 0:
                self.data_axes[0].set_xticks(
                    [old_ticks[0], selected_time, old_ticks[-1]]
                )

            xtick_labels = self.data_axes[0].get_xticklabels()
            if len(xtick_labels) > 1:
                xtick_labels[1].set_color(color=DefaultCursorColors.SELECTION)

            if self.tier_axes:
                xtick_labels = self.tier_axes[-1].get_xticklabels()
                if len(xtick_labels) > 1:
                    xtick_labels[1].set_color(
                        color=DefaultCursorColors.SELECTION)

            for axes in self.data_axes:
                current_ylim = axes.get_ylim()
                vline = axes.axvline(
                    x=selected_time,
                    linestyle=':',
                    color=DefaultCursorColors.SELECTION,
                    lw=1
                )
                self.selection_artists.append(vline)

                lines = axes.get_lines()
                colors = []
                yticks = axes.get_yticks()
                for line in lines:
                    if line in self.playback_cursor_lines:
                        continue
                    if line in self.selection_artists:
                        continue
                    if len(line.get_xdata()) <= 2:
                        continue

                    xdata = line.get_xdata()
                    if len(xdata) == 0:
                        continue

                    index = np.argmin(np.abs(xdata - selected_time))
                    y_value = line.get_ydata()[index]
                    color = line.get_color()

                    hline = axes.axhline(
                        y=y_value, linestyle=':', color=color, lw=1)
                    self.selection_artists.append(hline)
                    yticks = np.append(yticks, y_value)
                    colors.append(color)

                axes.set_yticks(yticks)

                labels = axes.get_yticklabels()
                ytick_lines = axes.yaxis.get_ticklines()
                for i, color in enumerate(colors):
                    if len(ytick_lines) > i*2+5:
                        ytick_lines[i*2+4].set_color(color)
                        ytick_lines[i*2+5].set_color(color)
                    if len(labels) > i+2:
                        labels[i+2].set_color(color)
                axes.set_ylim(current_ylim)
        else:
            old_ticks = self.original_xticks
            if len(old_ticks) > 2:
                self.data_axes[0].set_xticks([old_ticks[1], old_ticks[-2]])

        if selected_freq > -1:
            for i, name in enumerate(self.gui_config.data_axes):
                if "spectrogram" in name:
                    axes = self.data_axes[i]
                    yticks = axes.get_yticks()
                    axes.set_yticks(np.append(yticks, selected_freq))

                    hline = axes.axhline(
                        y=selected_freq,
                        linestyle=':',
                        color=DefaultCursorColors.SELECTION,
                        lw=1
                    )
                    self.selection_artists.append(hline)

                    labels = axes.get_yticklabels()
                    if len(labels) > 2:
                        labels[2].set_color(
                            color=DefaultCursorColors.SELECTION)
                    ytick_lines = axes.yaxis.get_ticklines()
                    if len(ytick_lines) > 5:
                        ytick_lines[4].set_color(
                            color=DefaultCursorColors.SELECTION)
                        ytick_lines[5].set_color(
                            color=DefaultCursorColors.SELECTION)

            for axes in self.tier_axes:
                vline = axes.axvline(
                    x=selected_time,
                    linestyle=':',
                    color=DefaultCursorColors.SELECTION,
                    lw=1
                )
                self.selection_artists.append(vline)

        # Force a synchronous draw to lock in the pixels immediately
        # and clear the MultiCursor's background cache.
        self.canvas.draw()
        if self.multicursor is not None:
            self.multicursor.background = None

    def plot_modality_axes(
        self,
        axes_number: int,
        axes_name: str,
        recording: Recording,
        xlim: tuple[float, float],
        zero_offset: float = 0,
        ylim: list[float, float] | None = None,
    ) -> None:
        """
        Plot modalities on a data_axes.
        """
        axes_params = self.gui_config.data_axes[axes_name]
        data_axes_params = self.gui_config.general_axes_params.data_axes
        plot_modality_names = axes_params.modalities

        if ylim is None:
            if data_axes_params is None and axes_params is None:
                ylim = None  # (-0.075, 1.075)
            elif data_axes_params.ylim is None and axes_params.ylim is None:
                if (
                    not data_axes_params.auto_ylim and
                    not axes_params.auto_ylim
                ):
                    ylim = None  # (-0.075, 1.075)
                else:
                    ylim = None
            elif axes_params.ylim is None:
                ylim = data_axes_params.ylim
            else:
                ylim = axes_params.ylim

        # TODO 0.23: this needs to work together with normalisation, maybe this
        # should in fact live inside of plot_timeseries instead of here?
        # This adjust y_limits in case the graphs are offset from each other.
        y_offset = 0
        if axes_params.y_offset is not None:
            y_offset = axes_params.y_offset
            ylim_adjustment = y_offset * len(plot_modality_names)
            if y_offset > 0:
                ylim = (ylim[0], ylim[1] + ylim_adjustment)
            else:
                ylim = (ylim[0] + ylim_adjustment, ylim[1])

        if axes_params.colors_in_sequence:
            colors = get_colors_in_sequence(len(plot_modality_names))
        else:
            colors = None
        for i, name in enumerate(plot_modality_names):
            modality = recording.modalities[name]
            plot_timeseries(
                self.data_axes[axes_number],
                modality.data,
                modality.timevector - zero_offset,
                xlim=xlim,
                ylim=ylim,
                color=colors[i],
                linestyle=(0, (i + 1, i + 1)),
                normalise=axes_params.normalisation,
                y_offset=i * y_offset,
                label=format_legend(
                    modality=modality,
                    index=i,
                    format_strings=axes_params.modality_names
                )
            )
            if axes_params.mark_peaks:
                mark_peaks(self.data_axes[axes_number],
                           modality,
                           self.xlim,
                           display_prominence_values=True,
                           time_offset=zero_offset)
            self.data_axes[axes_number].set_ylabel(axes_name)

        if axes_params.legend:
            self.data_axes[axes_number].legend(
                loc='upper left',
            )

    def draw_ultra_frame(
        self,
        recording: Recording,
        image_type: GuiImageType
    ) -> bool:
        """
        Draw the requested ultrasound frame into the secondary canvas.
        """
        if 'RawUltrasound' not in recording.modalities:
            return False

        if (
            (
                'frame_selection_index' not in recording.annotations or
                recording.annotations['frame_selection_index'] == -1
            )
            or image_type == GuiImageType.MEAN_IMAGE
        ):
            self.ultra_axes.clear()
            image_name = 'AggregateImage mean on RawUltrasound'
            if image_name in recording.statistics:
                stat = recording.statistics[image_name]
                image = stat.data
                self.ultra_axes.imshow(
                    image, interpolation='nearest', cmap='gray',
                    extent=(-image.shape[1] / 2 - .5, image.shape[1] / 2 + .5,
                            -.5, image.shape[0] + .5))
            return False

        elif (
            'frame_selection_index' in recording.annotations and
            recording.annotations['frame_selection_index'] >= 0
        ):
            self.ultra_axes.clear()
            index = recording.annotations['frame_selection_index']

            ultrasound = recording.modalities['RawUltrasound']
            if image_type == GuiImageType.FRAME:
                image = ultrasound.interpolated_image(index)
            elif image_type == GuiImageType.RAW_FRAME:
                image = ultrasound.raw_image(index)

            self.ultra_axes.imshow(
                image, interpolation='nearest', cmap='gray',
                extent=(-image.shape[1] / 2 - .5, image.shape[1] / 2 + .5,
                        -.5, image.shape[0] + .5))

            # TODO 0.24: implement these
            if self.gui_config.display_image_info:
                # image time, image index
                pass
            if self.gui_config.display_curve_values:
                # curve values at intersections
                pass

            # if image_type == GuiImageType.FRAME:
            #     self.kymography_clicker = clicker(
            #         ax=self.ultra_axes,
            #         classes=["event"],
            #         markers=["x"],
            #         linestyle="--")
            #     self.kymography_clicker.on_point_added(self.point_added_cb)
                # self.kymography_clicker.on_point_removed(
                #     self.point_removed_cb
                # )

            if (image_type == GuiImageType.FRAME
                    and 'Splines' in recording.modalities):
                splines = recording.modalities['Splines']
                index = recording.annotations['frame_selection_index']
                ultra = recording.modalities['RawUltrasound']
                timestamp = ultra.timevector[index]

                spline_index = np.argmin(
                    np.abs(splines.timevector - timestamp))

                # TODO 1.0: move this to reading splines/end of loading and
                # make the system warn the user when there is a creeping
                # discrepancy. also make it an integration test where
                # spline_test_token1 gets run and triggers this
                # ic(splines.timevector)
                # ic(ultra.timevector[:len(splines.timevector)])
                # time_diff = splines.timevector - \
                #     ultra.timevector[:len(splines.timevector)]
                # ic(np.diff(time_diff, n=1))
                # ic(np.max(np.abs(np.diff(time_diff, n=1))))

                epsilon = max((self.data_config.epsilon,
                               splines.time_precision))
                min_difference = abs(
                    splines.timevector[spline_index] - timestamp)
                # maybe this instead when loading data
                # str(number)[::-1].find('.') -> precision

                # ic(epsilon, splines.timevector[spline_index] - timestamp)
                # ic(splines.timevector[spline_index], timestamp)
                if min_difference > epsilon:
                    _logger.info("Splines out of synch in %s.",
                                 recording.basename)
                    _logger.info("Minimal difference: %f, epsilon: %f",
                                 min_difference, epsilon)

                spline_config = self.main_window.session.metadata.spline_config
                if spline_config.data_config:
                    limits = spline_config.data_config.ignore_points
                    plot_spline(self.ultra_axes,
                                splines.cartesian_spline(spline_index),
                                limits=limits)
                else:
                    plot_spline(self.ultra_axes,
                                splines.cartesian_spline(spline_index))
            else:
                _logger.info("No splines")

        self.ultra_canvas.draw_idle()
        return True

    def draw_raw_ultra_frame(
        self,
        recording: Recording,
        image_type: GuiImageType
    ) -> bool:
        """
        Display a raw ultrasound frame.
        """
        has_frame = False
        if recording.annotations['frame_selection_index'] > -1:
            has_frame = True
            ind = recording.annotations['frame_selection_index']
            array = recording.modalities['RawUltrasound'].data[ind, :, :]
        else:
            has_frame = False
            if recording.statistics['Aggregate mean on RawUltrasound']:
                array = recording.modalities[
                    'Aggregate mean on RawUltrasound'].data
            else:
                array = recording.modalities['RawUltrasound'].data[1, :, :]

        array = np.transpose(array)
        array = np.flip(array, 0).copy()
        array = array.astype(np.int8)
        self.ultra_axes.imshow(array, interpolation='nearest', cmap='gray')
        self.ultra_canvas.draw_idle()

        return has_frame

    def update_multicursor(self) -> None:
        """Update the MultiCursor after drawing."""
        if self.multicursor is not None:
            self.multicursor.disconnect()
            self.multicursor = None

        axes = self.data_axes + self.tier_axes
        if not axes:
            return

        self.multicursor = MultiCursor(
            self.canvas,
            axes=axes,
            color='deepskyblue',
            linestyle="--",
            lw=1
        )

    def update_playback_cursor(self, current_time: float) -> None:
        """
        Move the tracking cursor lines to the specified time.
        """
        if self.multicursor is not None:
            self.multicursor.disconnect()
            self.multicursor = None

        if self.playback_background is None:
            for line in self.playback_cursor_lines:
                line.set_visible(False)
                line.set_animated(True)

            self.canvas.draw()
            self.playback_background = self.canvas.copy_from_bbox(
                self.figure.bbox)

        self.canvas.restore_region(self.playback_background)

        for line in self.playback_cursor_lines:
            line.set_xdata([current_time, current_time])
            line.set_visible(True)
            line.axes.draw_artist(line)

        self.canvas.blit(self.figure.bbox)
        self.canvas.flush_events()

    def hide_playback_cursor(self) -> None:
        """Hide the tracking cursor lines on all axes."""
        for line in self.playback_cursor_lines:
            line.set_animated(False)
            line.set_visible(False)
        self.playback_background = None

        self.canvas.draw()

        self.update_multicursor()
