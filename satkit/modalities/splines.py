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

import logging
from pathlib import Path
from typing import Optional

import numpy as np
# from icecream import ic

from satkit.constants import CoordinateSystems
from satkit.data_structures import (
    Modality, ModalityData, ModalityMetaData, Recording)
from satkit.helpers.computational import (
    cartesian_to_polar, polar_to_cartesian)
from satkit.import_formats import read_splines

_modalities_logger = logging.getLogger('satkit.modalities')


class SplineMetadata(ModalityMetaData):
    """
    Metadata of a Splines Modality.
    """
    coordinates: CoordinateSystems
    number_of_sample_points: int
    confidence_exists: bool
    axisnames: tuple[str] = ('time', 'x-y', 'splinepoint')


class Splines(Modality):
    """
    Splines from 2D ultrasound data.
    """

    @classmethod
    def generate_name(cls, params: ModalityMetaData) -> str:
        return cls.__name__

    def __init__(self,
                 recording: Recording,
                 metadata: SplineMetadata,
                 data_path: Optional[Path] = None,
                 meta_path: Optional[Path] = None,
                 load_path: Optional[Path] = None,
                 parsed_data: Optional[ModalityData] = None,
                 time_offset: Optional[float] = None
                 ) -> None:

        # Initialise super only after ensuring meta is correct,
        # because latter may already end the run.
        super().__init__(
            recording=recording,
            metadata=metadata,
            data_path=data_path,
            meta_path=meta_path,
            load_path=load_path,
            parsed_data=parsed_data,
            time_offset=time_offset)

    def _read_data(self) -> ModalityData:
        return read_splines(self.data_path, self.metadata, self._time_offset)

    @property
    def data(self) -> np.ndarray:
        return super().data

    @data.setter
    def data(self, data) -> None:
        super()._data_setter(data)

    def get_meta(self) -> dict:
        return self.metadata

    @property
    def in_polar(self) -> np.ndarray:
        """
        Spline coordinates in polar coordiantes.

        Returns
        -------
        np.ndarray
            The coordinates
        """
        if self.metadata.coordinates is CoordinateSystems.POLAR:
            return self.data
        else:
            cartesian = self.data[:, 0:2, :]
            cartesian = cartesian.reshape([self.data.shape[0], -1])
            coords = np.apply_along_axis(
                cartesian_to_polar, 1, cartesian)
            polar = np.stack(
                [coords[:, 0, :], coords[:, 1, :], self.data[:, 2, :]], axis=1)
            return polar

    def cartesian_spline(self, index) -> np.ndarray:
        """
        Spline coordinates in Cartesian coordiantes.

        Returns
        -------
        np.ndarray
            The coordinates
        """
        if self.metadata.coordinates is CoordinateSystems.CARTESIAN:
            return self.data[index, :, :]
        else:
            return polar_to_cartesian(self.data[index, :, :], np.pi/2)

    @property
    def in_cartesian(self) -> np.ndarray:
        """
        Spline coordinates in Cartesian coordiantes.

        Returns
        -------
        np.ndarray
            The coordinates
        """
        if self.metadata.coordinates is CoordinateSystems.CARTESIAN:
            return self.data
        else:
            r_phi = self.data[:, 0:2, :]
            r_phi = r_phi.reshape([self.data.shape[0], -1])
            coords = np.apply_along_axis(
                polar_to_cartesian, 1, r_phi)
            cartesian = np.stack(
                [coords[:, 0, :], coords[:, 1, :], self.data[:, 2, :]], axis=1)
            return cartesian
