#
# Copyright (c) 2019-2023
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

# Built in packages
import logging
from pathlib import Path
from typing import Optional

# Local packages
from satkit.configuration import (data_run_params,
                                  set_exclusions_from_csv_file)
from satkit.constants import SourceSuffix
from satkit.data_structures import Recording

from .AAA_raw_ultrasound import (
    add_aaa_raw_ultrasound, parse_recording_meta_from_aaa_promptfile)
from .AAA_splines import add_splines
from .audio import add_audio
from .video import add_video

_AAA_logger = logging.getLogger('satkit.AAA')


def generate_aaa_recording_list(
        directory: Path,
        directory_structure: Optional[dict] = None):
    """
    Produce an array of Recordings from an AAA export directory.

    Prepare a list of Recording objects from the files exported by AAA into the
    named directory. File existence is tested for, and if crucial files are
    missing from a given recording it will be excluded.

    Each recording meta file (.txt, not US.txt) will be represented by a
    Recording object regardless of whether a complete set of files was found
    for the recording. Exclusion is marked with recording.excluded rather than
    not listing the recording. Log file will show reasons of exclusion.

    The processed files are recording meta: .txt, ultrasound meta: US.txt or
    .param, ultrasound: .ult, and audio waveform: .wav.

    If there is a `satkit_spline_import_config.yaml` present Splines modalities
    will be added to the Recordings, but any missing ones (or even all missing)
    are considered non-fatal.

    Additionally these will be added, but missing files are considered
    non-fatal avi video: .avi, and TextGrid: .textgrid.

    directory -- the path to the directory to be processed. Returns an array of
    Recording objects sorted by date and time
        of recording.
    """

    # TODO 1.1.: Deal with directory structure specifications.
    if directory_structure is not None:
        raise NotImplementedError

    ult_meta_files = sorted(directory.glob(
        '*' + SourceSuffix.AAA_ULTRA_META_OLD))
    if len(ult_meta_files) == 0:
        ult_meta_files = sorted(directory.glob(
            '*' + SourceSuffix.AAA_ULTRA_META_NEW))

    # this takes care of *.txt and *US.txt overlapping. Goal
    # here is to include also failed recordings with missing
    # ultrasound data in the list for completeness.
    ult_prompt_files = [
        prompt_file
        for prompt_file in directory.glob('*' + SourceSuffix.AAA_PROMPT)
        if not prompt_file in ult_meta_files]
    ult_prompt_files = sorted(ult_prompt_files)

    # strip file extensions off of filepaths to get the base names
    base_paths = [prompt_file.with_suffix('')
                  for prompt_file in ult_prompt_files]
    basenames = [Path(path).name for path in base_paths]
    recordings = [
        generate_ultrasound_recording(basename, Path(directory))
        for basename in basenames
    ]

    set_exclusions_from_csv_file(
        data_run_params['data properties']['exclusion list'],
        recordings)

    add_modalities(recordings, directory)

    return sorted(recordings, key=lambda
                  token: token.meta_data.time_of_recording)


def add_modalities(
        recording_list: list[Recording],
        directory: Path,
        wav_preload: bool = True,
        ult_preload: bool = False,
        video_preload: bool = False) -> None:
    """
    Add audio and raw ultrasound data to the recording.

    Keyword arguments:
    wavPreload -- boolean indicating if the .wav file is to be read into
        memory on initialising. Defaults to True.
    ultPreload -- boolean indicating if the .ult file is to be read into
        memory on initialising. Defaults to False. Note: these
        files are, roughly one to two orders of magnitude
        larger than .wav files.
    videoPreload -- boolean indicating if the .avi file is to be read into
        memory on initialising. Defaults to False. Note: these
        files are, yet again, roughly one to two orders of magnitude
        larger than .ult files.

    Throws KeyError if TimeInSecsOfFirstFrame is missing from the
    meta file: [directory]/basename + .txt.
    """
    for recording in recording_list:
        if not recording.excluded:
            _AAA_logger.info("Adding modalities to recording for %s.",
                             recording.basename)

            add_audio(recording, wav_preload)
            add_aaa_raw_ultrasound(recording, ult_preload)
            add_video(recording, video_preload)

    add_splines(recording_list, directory)


def generate_ultrasound_recording(basename: str, directory: Path):
    """
    Generate an UltrasoundRecording without Modalities.

    Arguments:
    basename -- name of the files to be read without type extensions but
        with path.

    KeywordArguments:
    directory -- path to files

    Returns an AaaUltrasoundRecording without any modalities.
    """

    _AAA_logger.info(
        "Building Recording object for %s in %s.", basename, directory)

    meta = parse_recording_meta_from_aaa_promptfile(
        (directory / basename).with_suffix('.txt'))

    textgrid = directory/basename
    textgrid = textgrid.with_suffix('.TextGrid')

    if textgrid.is_file():
        recording = Recording(
            meta_data=meta,
            textgrid_path=textgrid
        )
    else:
        recording = Recording(
            meta_data=meta,
        )

    return recording
