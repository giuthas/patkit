#!/usr/bin/env python3
#
# Copyright (c) 2019-2025
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
patkit example script
"""

from matplotlib.backends.backend_pdf import PdfPages

import numpy as np

from patkit import initialise_patkit
from patkit.annotations import (
    add_peaks, count_number_of_peaks, nearest_neighbours_in_downsampling,
    prominences_in_downsampling)
from patkit.annotations.peaks import annotations_to_dataframe

from patkit.metrics import (
    add_pd, add_spline_metric, downsample_metrics)
from patkit.modalities import RawUltrasound, Splines
from patkit.plot_and_publish import (
    publish_session_pdf, publish_distribution_data)
from patkit.plot_and_publish.publish import publish_distribution_data_seaborn
from patkit.data_processor import process_modalities
from patkit.utility_functions import log_elapsed_time


def main():
    """Simple main to run some publishing functions."""

    configuration, logger, session = initialise_patkit(
        path=path, config_file=config_file
    )

    data_run_config = configuration.data_run_config

    pd_arguments = {
        # 'norms': ['l0', 'l0.01', 'l0.1', 'l0.5', 'l1', 'l2',
        # 'l4', 'l10', 'l_inf', 'd'],
        'norms': ['l0', 'l0.5', 'l1', 'l2', 'l5', 'l_inf'],
        'timesteps': [1, 2, 3, 4, 5, 6, 7],
        # 'timesteps': [1],
        'mask_images': False,
        'pd_on_interpolated_data': False,
        'release_data_memory': True,
        'preload': True}

    spline_metric_arguments = {
        'metrics': ['annd', 'mpbpd', 'modified_curvature', 'fourier'],
        'timesteps': [3],
        'exclude_points': [2, 4],
        'release_data_memory': False,
        'preload': True}

    function_dict = {
        'PD': (add_pd,
               [RawUltrasound],
               pd_arguments),

        'SplineMetric': (add_spline_metric,
                         [Splines],
                         spline_metric_arguments)  # ,
    }

    process_modalities(recordings=session.recordings,
                       processing_functions=function_dict)

    if data_run_config.downsample:
        downsample_config = data_run_config.downsample

        for recording in session:
            downsample_metrics(recording, **downsample_config.model_dump())

    exclusion_list = ("water swallow", "bite plate")
    if data_run_config.peaks:
        modality_pattern = data_run_config.peaks.modality_pattern
        for recording in session:
            excluded = [prompt in recording.metadata.prompt
                        for prompt in exclusion_list]
            if any(excluded):
                print(
                    f"in patkit_publish.py: jumping over {recording.basename}")
                continue
            for modality_name in recording:
                if modality_pattern in modality_name:
                    add_peaks(
                        recording[modality_name],
                        configuration.data_run_config.peaks,
                    )

        metrics = data_run_config.pd_arguments.norms
        downsampling_ratios = data_run_config.downsample.downsampling_ratios
        number_of_peaks = count_number_of_peaks(
            session.recordings,
            metrics=metrics,
            downsampling_ratios=downsampling_ratios)

        reference = number_of_peaks[:, :, 0]

        # reference = reference.reshape(list(reference.shape).append(1))
        referees = number_of_peaks.copy()
        referees = np.moveaxis(referees, (0, 1, 2), (1, 2, 0))
        peak_number_ratio = referees/reference
        peak_number_ratio = np.moveaxis(
            peak_number_ratio, (0, 1, 2), (2, 1, 0))

        frequency_table = [recording['RawUltrasound'].sampling_rate
                           for recording in session
                           if 'RawUltrasound' in recording]
        frequency = np.average(frequency_table)
        frequencies = [f"{frequency/(i+1):.0f}" for i in range(7)]
        with PdfPages('figures/peak_number_ratios2.pdf') as pdf:
            publish_distribution_data(
                peak_number_ratio,
                plot_categories=metrics,
                within_plot_categories=frequencies,
                pdf=pdf,
                common_ylabel="Ratio of detected peaks",
                common_xlabel="Data sampling frequency (Hz)",
            )

        with PdfPages('figures/peak_numbers2.pdf') as pdf:
            number_of_peaks = np.moveaxis(
                number_of_peaks, (0, 1, 2), (1, 0, 2))
            publish_distribution_data(
                number_of_peaks,
                plot_categories=metrics,
                within_plot_categories=frequencies,
                pdf=pdf,
                common_ylabel="Number of peaks",
                common_xlabel="Data sampling frequency (Hz)",
            )

        with PdfPages('figures/peak_distances2.pdf') as pdf:
            publish_distribution_data(
                nearest_neighbours_in_downsampling(
                    session.recordings,
                    metrics=metrics,
                    downsampling_ratios=downsampling_ratios,),
                plot_categories=metrics,
                within_plot_categories=frequencies,
                pdf=pdf,
                legend_loc="upper left",
                common_ylabel="Mean absolute error of peak position",
                common_xlabel="Data sampling frequency (Hz)",
                horizontal_line=.075)

        with PdfPages('figures/peak_prominences2.pdf') as pdf:
            publish_distribution_data(
                prominences_in_downsampling(
                    session.recordings,
                    metrics=metrics,
                    downsampling_ratios=downsampling_ratios,),
                plot_categories=metrics,
                within_plot_categories=frequencies,
                pdf=pdf,
                legend_loc="upper left",
                common_ylabel="Mean peak prominence",
                common_xlabel="Data sampling frequency (Hz)",
            )

        with PdfPages('figures/seaborn_test.pdf') as pdf:
            dataframe = annotations_to_dataframe(
                session.recordings,
                modality_name=["RawUltrasound"],
                metrics=metrics,
                downsampling_ratios=downsampling_ratios,)
            publish_distribution_data_seaborn(
                dataframe,
                'prominence',
                plot_categories='metric',
                within_plot_categories='downsampling_ratio',
                pdf=pdf,
                category_titles=frequencies,
                common_ylabel="Mean peak prominence",
                common_xlabel="Data sampling frequency (Hz)",
            )
    logger.info('Data run ended.')

    publish_session_pdf(
        recording_session=session,
        timeseries_params=configuration.publish_config.timeseries_plot)

    log_elapsed_time(logger)


if __name__ == '__main__':
    main()
