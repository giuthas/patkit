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
Functions for loading previously saved/seen data.
"""

import logging
from pathlib import Path
from typing import Any, TextIO

import numpy as np
import nestedtext

from patkit.configuration import SessionConfig
from patkit.constants import PatkitConfigFile, PatkitSuffix
from patkit.data_import import (
    modality_adders, add_splines
)
from patkit.data_structures import (
    Answer, Exercise, ModalityData, Recording, Session
)
from patkit.data_structures.metadata_classes import FileInformation
from patkit.metrics import metrics, statistics

from .save_and_load_schemas import (
    AnswerLoadSchema, DataContainerListingLoadSchema,
    ExerciseLoadSchema, DataContainerLoadSchema,
    RecordingLoadSchema, SessionLoadSchema
)

_logger = logging.getLogger('patkit.recording_loader')


def _load_data_container_data_and_meta(
    path: Path,
    data_container_schema: DataContainerListingLoadSchema,
) -> tuple[FileInformation, DataContainerLoadSchema, Any]:
    """
    Load file information, meta data, and actual data for a DataContainer.

    Only a helper function, not for general use.
    """
    file_info = FileInformation(
        patkit_path=Path(""),
        patkit_data_file=data_container_schema.data_name,
        patkit_meta_file=data_container_schema.meta_name,
    )
    meta_path = path / data_container_schema.meta_name
    data_path = path / data_container_schema.data_name

    raw_input = nestedtext.load(meta_path)
    meta = DataContainerLoadSchema.model_validate(raw_input)

    saved_data = np.load(data_path)

    return file_info, meta, saved_data


def load_derived_modality(
        recording: Recording,
        path: Path,
        modality_schema: DataContainerListingLoadSchema
) -> None:
    """
    Load a saved derived Modality meta and data, and add them to the Recording.

    Parameters
    ----------
    recording : Recording
        The Recording the Modality will be added to.
    path : Path
        This is the path to the save files.
    modality_schema : DataContainerListingLoadSchema
        This contains the name of the meta and data files.
    """
    if not modality_schema.meta_name:
        _logger.info(
            "Looks like %s doesn't have a metafile for one of the Modalities.",
            modality_schema.data_name)
        _logger.info(
            "Assuming the Modality to be batch loaded, so skipping.")
        return

    file_info, meta, saved_data = _load_data_container_data_and_meta(
        path, modality_schema)

    modality_data = ModalityData(
        saved_data['data'], sampling_rate=saved_data['sampling_rate'],
        timevector=saved_data['timevector'])

    modality_constructor, parameter_schema = metrics[meta.object_type]
    for key in meta.parameters:
        if meta.parameters[key] == 'None':
            meta.parameters[key] = None
    parameters = parameter_schema(**meta.parameters)
    modality = modality_constructor(
        container=recording,
        file_info=file_info,
        parsed_data=modality_data,
        metadata=parameters)

    recording.add_modality(modality=modality)


def load_statistic(
        container: Recording | Session,
        path: Path,
        statistic_schema: DataContainerListingLoadSchema
) -> None:
    """
    Load a saved Statistic meta and data, and add them to the Recording.

    Parameters
    ----------
    owner : Recording
        The Recording the Statistic will be added to.
    path : Path
        This is the path to the save files.
    statistic_schema : DataContainerListingLoadSchema
        This contains the name of the meta and data files.
    """
    if not statistic_schema.meta_name:
        _logger.info(
            "Looks like %s doesn't have a metafile for one of the Statistics.",
            statistic_schema.data_name)
        _logger.info(
            "Assuming the Statistic to be batch loaded, so skipping.")
        return

    file_info, meta, saved_data = _load_data_container_data_and_meta(
        path, statistic_schema)

    statistic_data = saved_data['data']

    statistic_constructor, parameter_schema = statistics[meta.object_type]
    for key in meta.parameters:
        if meta.parameters[key] == 'None':
            meta.parameters[key] = None
    parameters = parameter_schema(**meta.parameters)
    statistic = statistic_constructor(
        container=container,
        file_info=file_info,
        parsed_data=statistic_data,
        metadata=parameters)

    container.add_statistic(statistic=statistic)


def read_recording_meta(
        filepath: str | Path | TextIO
) -> RecordingLoadSchema:
    """
    Read a Recording's saved metadata, validate it, and return it.

    Parameters
    ----------
    filepath : Union[str, Path, TextIO]
        This is passed to nestedtext.load.

    Returns
    -------
    RecordingLoadSchema
        The validated metadata.
    """
    raw_input = nestedtext.load(filepath)
    meta = RecordingLoadSchema.model_validate(raw_input)
    return meta


def load_recording(
    patkit_path: Path,
    recorded_path: Path,
    container: Session,
) -> Recording:
    """
    Load a recording from given Path.

    Parameters
    ----------
    patkit_path : Path
        Path to Recording's saved metadata file.
    recorded_path : Path
        Path to Recording's recorded data.

    Returns
    -------
    Recording
        A Recording object with most of its modalities loaded. Modalities like
        Splines that maybe stored in one file for several recordings aren't yet
        loaded at this point.

    Raises
    ------
    NotImplementedError
        If there is no previously saved metadata for the recording. This maybe
        handled by a future version of patkit, if it should prove necessary.
    """
    # decide which loader we will be using based on either filepath.patkit_meta
    # or config[''] in that order and document this behaviour. this way if the
    # data has previously been loaded patkit can decide itself what to do with
    # it and there is an easy place where to add processing
    # session/participant/whatever specific config. could also add guessing
    # based on what is present as the final fall back or as the option tried if
    # no meta and config has the wrong guess.

    meta_path = patkit_path.with_suffix(PatkitSuffix.META)
    if meta_path.is_file():
        # this is a list of Modalities, each with a data path and meta path
        recording_meta = read_recording_meta(patkit_path)
    else:
        # TODO: need to hand to the right kind of importer here.
        raise NotImplementedError(
            "Can't yet jump to a previously unloaded recording here.")

    file_info = FileInformation(
        recorded_path=recorded_path,
        patkit_path=meta_path.parent,
        patkit_meta_file=meta_path.name)
    recording = Recording(
        metadata=recording_meta.parameters,
        file_info=file_info,
        container=container
    )

    for modality in recording_meta.modalities:
        if modality in modality_adders:
            adder = modality_adders[modality]
            path = recorded_path/recording_meta.modalities[modality].data_name
            adder(recording, path=path)
        else:
            load_derived_modality(
                recording=recording,
                path=patkit_path.parent,
                modality_schema=recording_meta.modalities[modality])
    for statistic in recording_meta.statistics:
        load_statistic(
            recording,
            path=patkit_path.parent,
            statistic_schema=recording_meta.statistics[statistic])

    return recording


def load_recordings(
        patkit_path: Path,
        recorded_path: Path,
        container: Session,
        recording_metafiles: list[str] | None = None
) -> list[Recording]:
    """
    Load (specified) Recordings from directory.

    Parameters
    ----------
    directory : Path
        Path to the directory.
    recording_metafiles : Optional[list[str]]
        Names of the Recording metafiles. If omitted, all Recordings in the
        directory will be loaded.

    Returns
    -------
    list[Recording]
        List of the loaded Recordings.
    """
    if not recording_metafiles:
        recording_metafiles = patkit_path.glob(
            "*.Recording" + str(PatkitSuffix.META))

    recordings = [
        load_recording(
            patkit_path=patkit_path / name,
            recorded_path=recorded_path,
            container=container,
        )
        for name in recording_metafiles]

    add_splines(recordings, patkit_path)

    return recordings


def load_recording_session(
        directory: Path | str,
        session_config_path: Path | None = None
) -> Session:
    """
    Load a recording session from a directory.

    Parameters
    ----------
    directory: Path
        Root directory of the data.
    session_config_path : Path | None
        Path to the session configuration file. By default, None.

    Returns
    -------
    Session
        The loaded Session object.
    """
    # TODO: data_loader and this function should have clearer split of
    # responsibilities
    if isinstance(directory, str):
        directory = Path(directory)

    if session_config_path is None:
        session_config_path = directory / PatkitConfigFile.SESSION

    # filename = f"{directory.parts[-1]}{'.Session'}{PatkitSuffix.META}"
    # filepath = directory / filename

    filename = f"Session{PatkitSuffix.META}"
    filepath = directory / filename

    raw_input = nestedtext.load(filepath)
    meta = SessionLoadSchema.model_validate(raw_input)

    # if session_config_path.is_file():
    #     session_config = load_session_config(
    #         directory, session_config_path)
    # else:
    session_config = SessionConfig(
        data_source_name=meta.parameters.datasource_name,
        path_structure=meta.parameters.path_structure
    )

    file_info = FileInformation(
        patkit_meta_file=filename,
        patkit_path=directory,
        recorded_path=meta.parameters.recorded_path,
        recorded_meta_file=session_config_path.name
    )
    session = Session(
        name=meta.name,
        config=session_config,
        file_info=file_info
    )

    recordings = load_recordings(
        patkit_path=meta.parameters.patkit_path,
        recorded_path=meta.parameters.recorded_path,
        container=session,
        recording_metafiles=meta.recordings,
    )

    session.extend(recordings)

    return session


def load_answer(
        answer_dir: Path | str,
        exercise: Exercise
) -> Answer:
    """
    Load an Answer from a directory using schema validation.

    Parameters
    ----------
    answer_dir : Path | str
        The path to the saved answer directory.
    exercise : Exercise
        The parent Exercise context.

    Returns
    -------
    Answer
        The loaded Answer object.
    """
    if isinstance(answer_dir, str):
        answer_dir = Path(answer_dir)

    meta_path = answer_dir / PatkitConfigFile.ANSWER
    raw_input = nestedtext.load(meta_path)
    meta = AnswerLoadSchema.model_validate(raw_input)

    from patkit.data_structures import Answer
    answer = Answer(
        container=exercise,
        scenario=exercise.scenario,
        scramble=False,
        name=meta.name,
        author=meta.author,
        cursor=meta.cursor,
        time_created=meta.time_created,
        time_last_edited=meta.time_last_edited
    )

    from patkit.patgrid import PatGrid
    from patkit.constants import SourceSuffix
    for index, recording in enumerate(exercise.scenario.recordings):
        grid_path = answer_dir / (recording.basename + SourceSuffix.TEXTGRID)
        answer[index] = PatGrid(grid_path)

    return answer


def load_exercise(
        directory: Path | str,
        exercise_config_path: Path | None = None
) -> Exercise:
    """
    Load an exercise from a directory using schema validation.

    Parameters
    ----------
    directory: Path | str
        Root directory of the data.
    exercise_config_path : Path | None
        Path to the exercise configuration file. By default, None.

    Returns
    -------
    Exercise
        The loaded Exercise object.
    """
    if isinstance(directory, str):
        directory = Path(directory)

    if exercise_config_path is None:
        exercise_config_path = directory / PatkitConfigFile.EXERCISE

    raw_input = nestedtext.load(exercise_config_path)
    meta = ExerciseLoadSchema.model_validate(raw_input)

    session_dir = directory / meta.scenario_path
    scenario = load_recording_session(directory=session_dir)

    exercise = Exercise(
        scenario=scenario,
        time_created=meta.time_created,
        scrambling_method=meta.scrambling_method,
        index=meta.cursor
    )

    example_dir = directory / meta.example_dir
    exercise.example = load_answer(answer_dir=example_dir, exercise=exercise)

    for answer_dir_name in meta.answers:
        ans_dir = directory / answer_dir_name
        answer = load_answer(answer_dir=ans_dir, exercise=exercise)
        exercise[answer.name] = answer

    return exercise
