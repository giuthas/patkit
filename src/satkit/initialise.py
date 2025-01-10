#!/usr/bin/env python3
#
# Copyright (c) 2019-2025
# Pertti Palo, Scott Moisik, Matthew Faytak, and Motoki Saito.
#
# This file is part of Speech Articulation ToolKIT
# (see https://github.com/giuthas/satkit/).
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
# articles listed in README.markdown. They can also be found in
# citations.bib in BibTeX format.
#
"""
Main interface for running SATKIT.
"""

import sys
from argparse import Namespace
from logging import Logger
from pathlib import Path

from PyQt6 import QtWidgets

from satkit.annotations import add_peaks
from satkit.configuration import (
    apply_exclusion_list, load_exclusion_list, Configuration
)
from satkit.data_loader import load_data
from satkit.data_processor import (
    process_modalities,
    process_statistics_in_recordings
)
from satkit.data_structures import Session
from satkit.metrics import (
    add_aggregate_images, add_distance_matrices, add_pd,
    add_spline_metric, downsample_metrics_in_session
)
from satkit.modalities import RawUltrasound, Splines
from satkit.qt_annotator import PdQtAnnotator
from satkit.utility_functions import path_from_name, set_logging_level


def initialise_satkit(
        path: Path | str | None = None,
        config_file: Path | str | None = None,
        exclusion_file: Path | str | None = None,
        logging_level: int | None = None,
) -> tuple[Configuration, Logger, Session]:
    """
    Initialise the basic structures for running SATKIT.

    This sets up the argument parser, reads the basic configuration, sets up the
    logger, and loads the recorded and saved data into a Session. To initialise
    derived data run `add_derived_data`.

    Returns
    -------
    tuple[config, logger, session] where
        config is an instance of Configuration,
        logger is an instance of logging.Logger, and
        session is an instance of Session.
    """
    path = path_from_name(path)
    config_file = path_from_name(config_file)
    exclusion_file = path_from_name(exclusion_file)

    logger = set_logging_level(logging_level)
    config = Configuration(config_file)
    exclusion_list = None
    if exclusion_file is not None:
        exclusion_list = load_exclusion_list(exclusion_file)
    session = load_data(path, config)
    apply_exclusion_list(session, exclusion_list=exclusion_list)
    return config, logger, session


def add_derived_data(
        session: Session,
        config: Configuration,
) -> None:
    """
    Add derived data to the Session according to the Configuration.

    NOTE: This function will not delete existing data unless it is being
    replaced (and the corresponding `replace` parameter is `True`). This means
    that already existing derived data is retained.

    Added data types include Modalities, Statistics and Annotations.

    Parameters
    ----------
    session : Session
        The Session to add derived data to.
    config : Configuration
        The configuration parameters to use in deriving the new derived data.

    Returns
    -------
    None
    """
    data_run_config = config.data_run_config

    modality_operation_dict = {}
    if data_run_config.pd_arguments:
        pd_arguments = data_run_config.pd_arguments
        modality_operation_dict["PD"] = (
            add_pd,
            [RawUltrasound],
            pd_arguments.model_dump()
        )

    if data_run_config.aggregate_image_arguments:
        aggregate_image_arguments = data_run_config.aggregate_image_arguments
        modality_operation_dict["AggregateImage"] = (
            add_aggregate_images,
            [RawUltrasound],
            aggregate_image_arguments.model_dump()
        )

    if data_run_config.spline_metric_arguments:
        spline_metric_args = data_run_config.spline_metric_arguments
        modality_operation_dict["SplineMetric"] = (
            add_spline_metric,
            [Splines],
            spline_metric_args.model_dump()
        )

    process_modalities(recordings=session,
                       processing_functions=modality_operation_dict)

    statistic_operation_dict = {}
    if data_run_config.distance_matrix_arguments:
        distance_matrix_arguments = data_run_config.distance_matrix_arguments
        statistic_operation_dict["DistanceMatrix"] = (
            add_distance_matrices,
            ["AggregateImage mean on RawUltrasound"],
            distance_matrix_arguments.model_dump()
        )

    process_statistics_in_recordings(
        session=session,
        processing_functions=statistic_operation_dict)

    if data_run_config.downsample:
        downsample_metrics_in_session(recording_session=session,
                                      data_run_config=data_run_config)

    if data_run_config.peaks:
        modality_pattern = data_run_config.peaks.modality_pattern
        for recording in session:
            if recording.excluded:
                print(
                    f"in satkit.py: jumping over {recording.basename}")
                continue
            for modality_name in recording:
                # TODO make this deal with both strings and regexps as the
                # modality pattern
                if modality_pattern.search(modality_name):
                    add_peaks(
                        recording[modality_name],
                        config.data_run_config.peaks,
                    )


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
    args : Namespace
        The command line arguments from SatkitArgumentParser.
    """
    app = QtWidgets.QApplication(sys.argv)
    # Apparently the assignment to an unused variable is needed
    # to avoid a segfault.
    app.annotator = PdQtAnnotator(
        recording_session=session,
        display_tongue=True,
        config=config)
    sys.exit(app.exec())
