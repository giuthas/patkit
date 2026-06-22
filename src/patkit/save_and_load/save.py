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
Functions for saving patkit data.
"""

from collections import OrderedDict
from datetime import datetime
import logging
from pathlib import Path

import nestedtext
import numpy as np

from patkit.constants import (
    DEFAULT_ENCODING, OverwriteConfirmation, PatkitConfigFile,
    PATKIT_FILE_VERSION,
    PatkitDirectory, PatkitSuffix, SourceSuffix,
)
from patkit.data_structures import (
    Answer, Exercise, Manifest, Modality, Recording, Session, Statistic
)
from patkit.ui_callbacks import UiCallbacks
from patkit.data_structures.base_classes import AbstractDataContainer

from .save_and_load_schemas import nested_text_converters

_logger = logging.getLogger('patkit.save')


def _save_aggregator_meta(
        filepath: Path,
        meta: dict,
        confirmation: OverwriteConfirmation,
) -> None:
    if not filepath.exists() or confirmation in [
            OverwriteConfirmation.YES, OverwriteConfirmation.YES_TO_ALL]:
        try:
            nestedtext.dump(meta, filepath, converters=nested_text_converters)
            _logger.debug("Wrote file %s.", filepath)
        except OSError as e:
            _logger.critical(e)


def save_modality_data(
        modality: Modality,
        confirmation: OverwriteConfirmation
) -> tuple[str, OverwriteConfirmation]:
    """
    Save the data of a Modality.

    This saves only `ModalityData.data` and ModalityData.timevector.

    Returns the filename of the modality metadata file and confirmation flag
    for overwriting files.
    """
    _logger.debug("Saving data for %s.", modality.name)
    suffix = modality.name_underscored
    filename = f"{modality.recording.basename}.{suffix}{PatkitSuffix.DATA}"
    filepath = modality.recording.patkit_path/filename

    if filepath.exists():
        if confirmation is OverwriteConfirmation.NO_TO_ALL:
            return filename, confirmation

        if confirmation is not OverwriteConfirmation.YES_TO_ALL:
            confirmation = UiCallbacks.get_overwrite_confirmation(
                str(filepath))

    if not filepath.exists() or confirmation in [
            OverwriteConfirmation.YES, OverwriteConfirmation.YES_TO_ALL]:
        np.savez(
            filepath, data=modality.data,
            sampling_rate=modality.sampling_rate,
            timevector=modality.timevector)

        _logger.debug("Wrote file %s.", filename)

    return filename, confirmation


def save_modality_meta(
        modality: Modality, confirmation: OverwriteConfirmation
) -> tuple[str, OverwriteConfirmation]:
    """
    Save meta data and annotations for a Modality.

    Saved data includes sampling frequency and any processing metadata that is
    needed to reconstruct the Modality.
    """
    _logger.debug("Saving meta for %s.", modality.name)
    suffix = modality.name_underscored
    filename = f"{modality.recording.basename}.{suffix}"
    filename += PatkitSuffix.META
    filepath = modality.recording.patkit_path/filename

    if filepath.exists():
        if confirmation is OverwriteConfirmation.NO_TO_ALL:
            return filename, confirmation

        if confirmation is not OverwriteConfirmation.YES_TO_ALL:
            confirmation = UiCallbacks.get_overwrite_confirmation(
                str(filepath))

    meta = OrderedDict()
    meta['object_type'] = type(modality).__name__
    meta['name'] = modality.name
    meta['format_version'] = PATKIT_FILE_VERSION

    parameters = modality.get_meta().copy()
    meta['parameters'] = parameters

    if not filepath.exists() or confirmation in [
            OverwriteConfirmation.YES, OverwriteConfirmation.YES_TO_ALL]:
        try:
            nestedtext.dump(meta, filepath, converters=nested_text_converters)
            _logger.debug("Wrote file %s.", filename)
        # except nestedtext.NestedTextError as e:
        #     e.terminate()
        except OSError as e:
            _logger.critical(e)

    return filename, confirmation


def save_recording_meta(
        recording: Recording,
        confirmation: OverwriteConfirmation,
        modalities_saves: dict,
        statistics_saves: dict | None = None,
) -> tuple[str, OverwriteConfirmation]:
    """
    Save Recording meta.

    The meta dict should contain at least a list of the modalities this
    recording has and their saving locations.
    """
    _logger.debug(
        "Saving meta for recording %s.", recording.basename)
    filename = f"{recording.basename}{'.Recording'}{PatkitSuffix.META}"
    filepath = recording.patkit_path/filename

    if filepath.exists():
        if confirmation is OverwriteConfirmation.NO_TO_ALL:
            return filename, confirmation

        if confirmation is not OverwriteConfirmation.YES_TO_ALL:
            confirmation = UiCallbacks.get_overwrite_confirmation(
                str(filepath))

    meta = OrderedDict()
    meta['object_type'] = type(recording).__name__
    meta['name'] = recording.basename
    meta['format_version'] = PATKIT_FILE_VERSION
    meta['parameters'] = recording.metadata.model_dump()
    meta['modalities'] = modalities_saves
    meta['statistics'] = statistics_saves

    _save_aggregator_meta(
        filepath=filepath, meta=meta, confirmation=confirmation)

    return filename, confirmation


def save_modalities(
        recording: Recording, confirmation: OverwriteConfirmation | None
) -> tuple[dict, OverwriteConfirmation]:
    """
    Save derived Modalities and gather meta for all Modalities.

    Returns a dictionary of the data and meta paths of the Modalities.
    """
    recording_meta = {}
    for modality_name in recording:
        modality_meta = {}
        modality = recording[modality_name]
        if modality.is_derived:
            (modality_meta['data_name'], confirmation) = save_modality_data(
                modality, confirmation)
            (modality_meta['meta_name'], confirmation) = save_modality_meta(
                modality, confirmation)
        else:
            modality_meta['data_name'] = str(modality.recorded_data_path.name)
            if modality.recorded_meta_path:
                modality_meta['meta_name'] = str(
                    modality.recorded_meta_path.name)
            else:
                modality_meta['meta_name'] = None
        recording_meta[modality_name] = modality_meta
    return recording_meta, confirmation


def save_statistic_data(
        statistic: Statistic,
        confirmation: OverwriteConfirmation
) -> tuple[str, OverwriteConfirmation]:
    """
    Save the data of a Modality.

    This saves only Statistic.data.

    Returns the filename of the
    """
    _logger.debug("Saving data for %s.", statistic.name)
    if not statistic.patkit_data_name:
        suffix = statistic.name_underscored
        filename = f"{statistic.container.name}.{suffix}{PatkitSuffix.DATA}"
        statistic.patkit_data_name = filename

    filepath = statistic.patkit_data_path
    if filepath.exists():
        if confirmation is OverwriteConfirmation.NO_TO_ALL:
            return statistic.patkit_data_name, confirmation

        if confirmation is not OverwriteConfirmation.YES_TO_ALL:
            confirmation = UiCallbacks.get_overwrite_confirmation(
                str(filepath))

    if not filepath.exists() or confirmation in [
            OverwriteConfirmation.YES, OverwriteConfirmation.YES_TO_ALL]:
        np.savez(
            filepath, data=statistic.data)

        _logger.debug("Wrote file %s.", statistic.patkit_data_path)

    return statistic.patkit_data_name, confirmation


def save_statistic_meta(
        statistic: Statistic, confirmation: OverwriteConfirmation
) -> tuple[str, OverwriteConfirmation]:
    """
    Save meta data and annotations for a Modality.

    Saved data includes sampling frequency and any processing metadata that is
    needed to reconstruct the Modality.
    """
    _logger.debug("Saving meta for %s.", statistic.name)
    if not statistic.patkit_meta_name:
        suffix = statistic.name_underscored
        filename = f"{statistic.container.name}.{suffix}{PatkitSuffix.META}"
        statistic.patkit_meta_name = filename

    filepath = statistic.patkit_meta_path

    if filepath.exists():
        if confirmation is OverwriteConfirmation.NO_TO_ALL:
            return statistic.patkit_meta_name, confirmation

        if confirmation is not OverwriteConfirmation.YES_TO_ALL:
            confirmation = UiCallbacks.get_overwrite_confirmation(
                str(filepath))

    meta = OrderedDict()
    meta['object_type'] = type(statistic).__name__
    meta['name'] = statistic.name
    meta['format_version'] = PATKIT_FILE_VERSION

    parameters = statistic.get_meta().copy()
    meta['parameters'] = parameters

    if not filepath.exists() or confirmation in [
            OverwriteConfirmation.YES, OverwriteConfirmation.YES_TO_ALL]:
        try:
            nestedtext.dump(meta, filepath, converters=nested_text_converters)
            _logger.debug("Wrote file %s.",
                          statistic.patkit_meta_path)
        # except nestedtext.NestedTextError as e:
        #     e.terminate()
        except OSError as e:
            _logger.critical(e)

    return statistic.patkit_meta_name, confirmation


def save_statistics(
        aggregator: AbstractDataContainer,
        confirmation: OverwriteConfirmation | None
) -> tuple[dict, OverwriteConfirmation]:
    """
    Save Statistics and gather meta for all Statistics.

    Returns a dictionary of the data and meta paths of the Statistics.
    """
    recording_meta = {}
    for statistic_name in aggregator.statistics:
        statistic_meta = {}
        statistic = aggregator.statistics[statistic_name]
        if statistic.patkit_path is None:
            statistic.patkit_path = ""
        (statistic_meta['data_name'], confirmation) = save_statistic_data(
            statistic, confirmation)
        (statistic_meta['meta_name'], confirmation) = save_statistic_meta(
            statistic, confirmation)
        recording_meta[statistic_name] = statistic_meta
    return recording_meta, confirmation


def save_recordings(
        recordings: list[Recording],
        confirmation: OverwriteConfirmation | None,
        save_excluded: bool = True
) -> tuple[list[str], OverwriteConfirmation]:
    """
    Save derived data modalities for each Recording.
    """
    metafiles = []
    for recording in recordings:
        if save_excluded or not recording.excluded:
            if recording.patkit_path is None:
                recording.patkit_path = ""
            modalities_saves, confirmation = save_modalities(
                recording=recording,
                confirmation=confirmation,)
            statistics_saves, confirmation = save_statistics(
                aggregator=recording,
                confirmation=confirmation
            )
            metafile, confirmation = save_recording_meta(
                recording=recording,
                modalities_saves=modalities_saves,
                statistics_saves=statistics_saves,
                confirmation=confirmation)
            metafiles.append(metafile)

    return metafiles, confirmation


def save_session_meta(
        session: Session,
        recording_meta_files: list[str],
        confirmation: OverwriteConfirmation,
        statistics_saves: dict | None = None,
) -> tuple[str, OverwriteConfirmation]:
    """
    Save recording session metadata.

    The meta dict should contain at least a list of the recordings in this
    session and their saving locations.
    """
    _logger.debug(
        "Saving meta for session %s.", session.name)
    filename = f"Session{PatkitSuffix.META}"
    filepath = session.patkit_path/filename

    if filepath.exists():
        if confirmation is OverwriteConfirmation.NO_TO_ALL:
            return filename, confirmation

        if confirmation is not OverwriteConfirmation.YES_TO_ALL:
            confirmation = UiCallbacks.get_overwrite_confirmation(
                str(filepath))

    # TODO 1.0: This should really be a model dump not a dict.
    meta = OrderedDict()
    meta['object_type'] = type(session).__name__
    meta['name'] = session.name
    meta['format_version'] = PATKIT_FILE_VERSION

    parameters = OrderedDict()
    parameters['patkit_path'] = str(session.patkit_path.resolve())
    parameters['recorded_path'] = str(session.recorded_path.resolve())
    parameters['datasource_name'] = session.metadata.data_source_name.value
    parameters['path_structure'] = session.config.path_structure.model_dump()

    meta['parameters'] = parameters
    meta['recordings'] = recording_meta_files
    meta['statistics'] = statistics_saves

    _save_aggregator_meta(
        filepath=filepath, meta=meta, confirmation=confirmation)

    return filename, confirmation


def save_manifest(session: Session) -> None:
    """
    Save the manifest file.

    The manifest file contains a list of PATKIT scenarios that refer to the
    recorded data. These maybe used to backtrack to already calculated
    Modalities and Statistics to save time.

    This function will first read any existing manifest file and then append
    the current Session's PATKIT meta to the file if it is not already
    included.

    Parameters
    ----------
    session : Session
        The session to be added to the manifest.
    """
    manifest_path = session.recorded_path/PatkitConfigFile.MANIFEST

    manifest = Manifest(manifest_path)
    # Manifest.append is safe against duplicates.
    manifest.append(session.patkit_meta_path)
    # Always write in case there is an update to the file format.
    manifest.save()


def save_recording_session(
        session: Session) -> tuple[str, OverwriteConfirmation]:
    """
    Save a recording session.
    """
    _logger.debug(
        "Saving recording session %s.", session.name)
    # if session.patkit_path is None:
    #     print("patkit path is none")
    #     sys.exit()
    #     session.patkit_path = session.recorded_path
    recording_meta_files, confirmation = save_recordings(
        recordings=session.recordings, confirmation=None)
    statistics_saves, confirmation = save_statistics(
        aggregator=session,
        confirmation=confirmation
    )
    meta_name, confirmation = save_session_meta(
        session=session,
        recording_meta_files=recording_meta_files,
        confirmation=confirmation,
        statistics_saves=statistics_saves,
    )
    save_manifest(session)

    return meta_name, confirmation


def save_answer(answer: Answer) -> None:
    """
    Save an Answer's TextGrids and metadata to disk.
    Path is natively computed by the Answer object.
    """
    output_dir = answer.patkit_data_path
    # TODO 1.0: is this in the right place? should this not be updated in the
    # ui rather than here?
    answer.metadata.time_last_edited = datetime.now().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO 1.0: This should really be a model dump not a dict.
    metadata = {
        "name": answer.name,
        "author": answer.metadata.author,
        "cursor": answer.cursor,
        "time_created": answer.metadata.time_created,
        "time_last_edited": answer.metadata.time_last_edited
    }

    meta_path = output_dir / PatkitConfigFile.ANSWER
    nestedtext.dump(
        metadata, meta_path, converters=nested_text_converters
    )

    for index, patgrid in enumerate(answer):
        recording = answer.scenario.recordings[index]
        grid_path = output_dir / (
            recording.basename + SourceSuffix.TEXTGRID
        )
        with open(grid_path, 'w', encoding=DEFAULT_ENCODING) as outfile:
            outfile.write(patgrid.format_long())


def save_exercise(exercise: Exercise) -> None:
    """
    Save an Exercise, its metadata, example, and all Answers to disk.
    """
    base_dir = exercise.patkit_path
    base_dir.mkdir(parents=True, exist_ok=True)

    example_dir_name = PatkitDirectory.EXAMPLE
    scenario_path_str = str(
        exercise.scenario.patkit_path.relative_to(base_dir, walk_up=True)
    )

    answer_names = [answer.name for answer in exercise.values()]

    # TODO 1.0: This should really be a model dump not a dict.
    metadata = {
        "scenario_path": scenario_path_str,
        "time_created": exercise.metadata.time_created,
        "scrambling_method": str(exercise.metadata.scrambling_method),
        "cursor": exercise.cursor,
        "example_dir": example_dir_name,
        "answers": answer_names,
    }

    meta_path = base_dir / PatkitConfigFile.EXERCISE
    nestedtext.dump(
        metadata, meta_path, converters=nested_text_converters
    )

    save_answer(answer=exercise.example)

    for answer in exercise.values():
        save_answer(answer=answer)
