#!/usr/bin/env python3
#
# Copyright (c) 2019-2024
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
Downsampling of metrics and possibly other timeseries data.
"""

from satkit.data_structures import (
    Modality, ModalityData, ModalityMetaData, Recording)


def downsample_modality(
        modality: Modality,
        downsampling_ratio: int,
        metadata: ModalityMetaData
) -> Modality:
    """
    Downsample the Modality by the given ratio and return results as a new
    Modality. 

    Parameters
    ----------
    modality : Modality
        The original Modality
    downsampling_ratio : int
        Ratio by which to downsample

    Returns
    -------
    Modality
        This Modality will match the type and metadata of the original, but
        will have the metadata fields that describe downsampling updated
        correctly. The Modality's data and timevector will have been
        downsampled its and name will show the downsampling ratio used.
    """
    data = modality.data[::downsampling_ratio]
    timevector = modality.timevector[::downsampling_ratio]
    sampling_rate = modality.sampling_rate/downsampling_ratio

    modality_data = ModalityData(
        data=data, timevector=timevector, sampling_rate=sampling_rate)

    return modality.__class__(
        modality.recording,
        parsed_data=modality_data,
        metadata=metadata,
        meta_path=modality.meta_path,
        load_path=modality.load_path,
        time_offset=modality.time_offset)


def downsample_metrics(
        recording: Recording,
        modality_pattern: str,
        downsampling_ratios: tuple[int],
        match_timestep: bool = True
) -> None:
    """
    Apply downsampling to Modalities matching the pattern and add them back to
    the Recording.

    Parameters
    ----------
    recording : Recording
        The Recording which contains the Modalities and to which the new
        downsampled modalities will be added.
    modality_pattern : str
        Simple search string to used to find the modalities.
    downsampling_ratios : tuple[int]
        Which downsampling ratios should be attempted. Depending on the next
        parameter all might not actually be used.
    match_timestep : bool, optional
        If the timestep of the Modality to be downsampled should match the
        downsampling_ratio, by default True

    Raises
    ------
    NotImplementedError
        For now only match_timestep = True is allowed.
    """

    modalities = [recording[key]
                  for key in recording
                  if modality_pattern in key]

    if match_timestep:
        modalities = [
            modality for modality in modalities
            if modality.metadata.timestep in downsampling_ratios]

        for modality in modalities:
            downsampling_ratio = modality.metadata.timestep
            metadata = modality.metadata.model_copy()
            metadata.is_downsampled = True
            metadata.downsampling_ratio = downsampling_ratio
            metadata.timestep_matched_downsampling = (
                downsampling_ratio == metadata.timestep)
            name = modality.__class__.generate_name(metadata)
            if name not in recording:
                downsampled = downsample_modality(
                    modality, downsampling_ratio, metadata)
                recording.add_modality(downsampled)

    else:
        raise NotImplementedError(
            "Downsampling without matching the downsampling "
            "step to the timestep of the modality has not been "
            "implemented yet.")
