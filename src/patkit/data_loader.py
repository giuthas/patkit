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
Import or load a Session from a directory.
"""

import logging
import sys
from pathlib import Path

from patkit.audio_processing import MainsFilter
from patkit.configuration import (
    Configuration, PathStructure, SessionConfig
)
from patkit.constants import (
    DatasourceNames, SourceSuffix, PatkitSuffix, PatkitConfigFile)
from patkit.data_import import (
    generate_aaa_recording_list, generate_wav_recording_list,
    load_session_config
)
from patkit.data_structures import (
    FileInformation, Session)
from patkit.errors import NoImporterError
from patkit.save_and_load import load_recording_session

_logger = logging.getLogger('patkit.scripting')

# TODO 0.27: change the name of this file to data_importer and move it to a
# more appropriate submodule?


def load_data(configuration: Configuration) -> Session:
    """
    Handle loading data from individual files or a previously saved session.

    Parameters
    ----------
    configuration : Configuration
        patkit configuration.

    Returns
    -------
    Session
        The generated Session object with the exclusion list applied.
    """
    recorded_path = configuration.data_config.recorded_data_path
    patkit_path = configuration.config_paths.path

    # TODO 0.25 Should not blindly assume that sampling frequency is 44100!
    if configuration.data_config.mains_frequency:
        MainsFilter.generate_mains_filter(
            44100,
            configuration.data_config.mains_frequency)
    else:
        print(
            "No mains frequency specified. Guessing 60 Hz. Please "
            "check if this is correct where the data was recorded.")
        MainsFilter.generate_mains_filter(44100, 60)

    if patkit_path is not None:
        meta_files = patkit_path.glob("*" + PatkitSuffix.META)
    else:
        meta_files = recorded_path.glob("*" + PatkitSuffix.META)

    if len(list(meta_files)) == 0:
        _logger.debug("Reading session from %s.", recorded_path)
        session = read_recorded_session_from_dir(recorded_path)
        session.patkit_path = configuration.config_paths.path
    else:
        _logger.debug("Loading session from %s.", patkit_path)
        session = load_recording_session(patkit_path)

    for recording in session:
        recording.after_modalities_init()

    return session


def read_recorded_session_from_dir(
        recorded_data_path: Path,
        detect_beep: bool = False
) -> Session:
    """
    Read recorded data from a directory.

    This function tries to guess which importer to use.

    Parameters
    ----------
    recorded_data_path : Path
        Path to the recorded data.
    detect_beep : bool, optional
        Should the 1kHz beep detection be run on audio data, by default False

    Returns
    -------
    Session
        The Session object containing the recorded data. Derived data should be
        added with a separate function call.

    Raises
    ------
    NotImplementedError
        RASL data is not yet loadable.
    NotImplementedError
        Unrecognised data sources will raise an error.
    """
    if not recorded_data_path.exists():
        print(f"Recorded data directory not found: {recorded_data_path}.")
        sys.exit()

    containing_dir = recorded_data_path.parts[-1]
    session_config_path = recorded_data_path / PatkitConfigFile.SESSION
    session_meta_path = recorded_data_path / (containing_dir + '.Session' +
                                              PatkitSuffix.META)
    if session_meta_path.is_file():
        session = load_recording_session(
            recorded_data_path, session_config_path
        )
        return session

    # TODO 1.0: if Sessions are no longer the highest possible container tier,
    # this logic needs to change.
    file_info = FileInformation(
        recorded_path=recorded_data_path,
        recorded_meta_file=session_config_path.name,
        is_top_level_object=True,
    )
    if session_config_path.is_file():
        session_config = load_session_config(
            recorded_data_path, session_config_path)

        match session_config.data_source_name:
            case DatasourceNames.AAA:
                session = Session(
                    name=containing_dir, config=session_config,
                    file_info=file_info)
                recordings = generate_aaa_recording_list(
                    directory=recorded_data_path,
                    container=session,
                    import_config=session_config)
                session.extend(recordings)

                return session
            case DatasourceNames.RASL:
                raise NotImplementedError(
                    "Loading RASL data hasn't been implemented yet.")
            case _:
                raise NotImplementedError(
                    f"Unrecognised data source: "
                    f"{session_config.data_source_name}")

    if list(recorded_data_path.glob('*' + SourceSuffix.AAA_ULTRA)):
        paths = PathStructure(root=recorded_data_path)
        session_config = SessionConfig(
            data_source_name=DatasourceNames.AAA,
            path_structure=paths)

        session = Session(
            name=containing_dir, config=session_config,
            file_info=file_info)

        recordings = generate_aaa_recording_list(
            directory=recorded_data_path,
            container=session,
            import_config=session_config,
            detect_beep=detect_beep,
        )
        session.extend(recordings)

        return session

    if list(recorded_data_path.glob('*' + SourceSuffix.WAV)):
        paths = PathStructure(root=recorded_data_path)
        session_config = SessionConfig(
            data_source_name=DatasourceNames.WAV,
            path_structure=paths)

        session = Session(
            name=containing_dir, config=session_config,
            file_info=file_info)

        recordings = generate_wav_recording_list(
            directory=recorded_data_path,
            container=session,
            import_config=session_config,
            detect_beep=detect_beep,
        )
        session.extend(recordings)

        return session

    _logger.error(
        'Could not find a suitable importer: %s', recorded_data_path)
    raise NoImporterError(
        f"Could not find a suitable importer for data at: "
        f"{recorded_data_path}")
