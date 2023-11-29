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
"""SATKIT's core datastructures."""

# Built in packages
import abc
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from icecream import ic

# Numerical arrays and more
import numpy as np
from pydantic import BaseModel

# Praat textgrids
import textgrids

from satkit.configuration import PathStructure, SessionConfig
from satkit.constants import SatkitSuffix
from satkit.errors import MissingDataError, ModalityError, OverWriteError
from satkit.satgrid import SatGrid

_datastructures_logger = logging.getLogger('satkit.data_structures')


class RecordingMetaData(BaseModel):
    """Basic metadata that any Recording should reasonably have."""
    prompt: str
    time_of_recording: datetime
    participant_id: str
    basename: str
    path: Path


@dataclass
class ModalityData:
    """
    Data passed from Modality generation into Modality.

    None of the fields are optional. This class represents already loaded data.

    Axes order for the data field is [time, coordinate axes and datatypes,
    datapoints] and further structure. For example stereo audio data would be
    [time, channels] or just [time] for mono audio. For a more complex example,
    splines from AAA have [time, x-y-confidende, spline points] or [time,
    r-phi-confidence, spline points] for data in polar coordinates.
    """
    data: np.ndarray
    sampling_rate: float
    timevector: np.ndarray


class ModalityMetaData(BaseModel):
    """Baseclass of Modalities' metadata classes."""
    parent_name: Optional[str] = None


@dataclass
class RecordingSession:
    # class RecordingSession(BaseModel):
    """
    The meta and Recordings of a recording session.
    """
    name: str
    paths: PathStructure
    config: SessionConfig
    recordings: list['Recording']


class Recording:
    """
    A Recording contains 0-n synchronised Modalities.

    The recording also contains the non-modality 
    specific metadata (participant, speech content, etc) 
    as a dictionary, as well as the textgrid for the whole recording.

    In inheriting classes call self._read_textgrid() after calling
    super.__init__() (with correct arguments) and doing any updates
    to self.meta['textgrid'] that are necessary.
    """

    def __init__(self,
                 meta_data: RecordingMetaData,
                 excluded: bool = False,
                 textgrid_path: Union[str, Path] = "") -> None:
        """
        Construct a mainly empty recording without modalities.

        Modalities and annotations get added after constructions with their own
        add_[modality or annotation] functions.

        Parameters
        ----------
        meta_data : RecordingMetaData
            Some of the contents of the meta data are avaible as properties.
        excluded : bool, optional
            _description_, by default False
        textgrid_path : Union[str, Path], optional
            _description_, by default ""
        """
        self.excluded = excluded

        self.meta_data = meta_data

        self.textgrid_path = textgrid_path
        if not self.textgrid_path:
            self.textgrid_path = meta_data.path.joinpath(
                meta_data.basename + ".TextGrid")
        self.textgrid = self._read_textgrid()
        self.satgrid = SatGrid(self.textgrid)

        self.modalities = {}
        self.annotations = {}

    @property
    def path(self) -> Path:
        """Path to this recording."""
        return self.meta_data.path

    @path.setter
    def path(self, path: Path) -> None:
        self.meta_data.path = path

    @property
    def basename(self) -> str:
        """Filename of this Recording without extensions."""
        return self.meta_data.basename

    @basename.setter
    def basename(self, basename: str) -> None:
        self.meta_data.basename = basename

    def _read_textgrid(self) -> textgrids.TextGrid:
        """
        Read the textgrid specified in self.meta.

        If file does not exist or reading fails, recovery is attempted 
        by logging an error and creating an empty textgrid for this 
        recording.
        """
        textgrid = None
        if self.textgrid_path.is_file():
            try:
                textgrid = textgrids.TextGrid(self.textgrid_path)
                _datastructures_logger.info("Read textgrid in %s.",
                                            self.textgrid_path)
            except Exception as exception:
                _datastructures_logger.critical(
                    "Could not read textgrid in %s.", self.textgrid_path)
                _datastructures_logger.critical(
                    "Failed with: %s.", str(exception))
                _datastructures_logger.critical("Creating an empty textgrid "
                                                + "instead.")
                textgrid = textgrids.TextGrid()
        else:
            notice = 'Note: ' + str(self.textgrid_path) + " did not exist."
            _datastructures_logger.warning(notice)
            _datastructures_logger.warning("Creating an empty textgrid "
                                           + "instead.")
            textgrid = textgrids.TextGrid()
        return textgrid

    def identifier(self) -> str:
        """
        Generate a unique identifier for this Recording from metadata.

        Returns
        -------
        str
            prompt followed by time of recording.
        """
        return (f"{self.meta_data.prompt} "
                f"{str(self.meta_data.time_of_recording)}")

    def exclude(self) -> None:
        """
        Set self.excluded to True with a method.

        This method exists to facilitate list comprehensions being used
        for excluding recordings e.g. 
        [recording.exclude() for recording in recordings if in some_list].
        """
        self.excluded = True

    def write_textgrid(self, filepath: Path = None) -> None:
        """
        Save this recording's textgrid to file.

        Keyword argument:
        filepath -- string specifying the path and name of the 
            file to be written. If filepath is not specified, this 
            method will try to overwrite the textgrid speficied in 
            self.meta.

            If filepath is specified, subsequent calls to this 
            function will write into the new path rather than 
            the original one.
        """
        try:
            if filepath:
                self.textgrid_path = filepath
                self.textgrid.write(filepath)
            else:
                self.textgrid.write(self.textgrid_path)
        except Exception as exception:
            _datastructures_logger.critical(
                "Could not write textgrid to %s.", str(self.textgrid_path))
            _datastructures_logger.critical(
                "TextGrid save failed with error: %s", str(exception))

    # should the modalities dict be accessed as a property?
    def add_modality(
            self, modality: 'Modality', replace: bool = False) -> None:
        """
        This method adds a new Modality object to the Recording.

        Replacing a modality has to be specified otherwise if a
        Modality with the same name already exists in this Recording
        and the replace argument is not True, an Error is raised. 

        Arguments:
        modality -- object of type Modality to be added to 
            this Recording.

        Keyword arguments:
        replace -- a boolean indicating if an existing Modality should
            be replaced.
        """
        name = modality.name

        if name in self.modalities and not replace:
            raise ModalityError(
                "A modality named " + name +
                " already exists and replace flag was False.")
        elif replace:
            self.modalities[name] = modality
            _datastructures_logger.debug("Replaced modality %s.", name)
        else:
            self.modalities[name] = modality
            _datastructures_logger.debug("Added new modality %s.", name)

    def __str__(self) -> str:
        """
        Bare minimum string representation of the Recording.

        Returns
        -------
        string
            'Recording [basename]'
        """
        return f"Recording {self.basename}"


class Modality(abc.ABC):
    """
    Abstract superclass for all data Modality classes.
    """

    def __init__(self,
                 recording: Recording,
                 parsed_data: Optional[ModalityData] = None,
                 metadata: Optional[ModalityMetaData] = None,
                 data_path: Optional[Path] = None,
                 meta_path: Optional[Path] = None,
                 load_path: Optional[Path] = None,
                 time_offset: Optional[float] = None
                 ) -> None:
        """
        Modality constructor.

        Positional arguments:
        recording -- the containing Recording.

        Keyword arguments:
        data_path -- path of the data file
        load_path -- path of data when saved by SATKIT - both data and metadata
        parent -- the Modality this one was derived from. None means this 
            is an underived data Modality.
        parsed_data -- ModalityData object containing waveform, sampling rate,
            and either timevector and/or time_offset. 
        parsed_data -- a ModalityData object containing parsed data 
            that's been either read from file, loaded from file 
            (previously saved by SATKIT), or calculated from another modality.
            Providing a timevector 
            overrides any time_offset value given, but in absence of a 
            timevector the time_offset will be applied on reading the data 
            from file. 
        time_offset -- offset of this modality in relation to the Recordings
            baseline - usually the audio track. This will be ignored if 
            parsed_data exists and effectively overridden by 
            parsed_data.timevector.
        """
        self.recording = recording
        self.data_path = data_path
        self._meta_path = meta_path  # self.meta_path is a property
        self.load_path = load_path

        self.metadata = metadata

        if parsed_data:
            self._data = parsed_data.data
            self._sampling_rate = parsed_data.sampling_rate
            self._timevector = parsed_data.timevector
        else:
            self._data = None
            self._sampling_rate = None
            self._timevector = None

        if self._timevector is None:
            self._time_offset = time_offset
        else:
            self._time_offset = self._timevector[0]

        # This is a property which when set to True will also set
        # parent.excluded to True.
        self.excluded = False
        self._time_precision = None

    def _get_data(self) -> ModalityData:
        # TODO: Provide a way to force the data to be derived.
        # this would be used when parent modality has updated in some way
        if self.data_path:
            return self._read_data()
        elif self.load_path:
            return self._load_data()
        elif self.metadata.parent_name:
            return self._derive_data()
        else:
            raise MissingDataError(
                "Asked to get data but have no path and no parent Modality.\n"
                + "Don't know how to solve this.")

    # TODO: should these really return a value rather than
    # just write the fields? And if return a value, why not
    # ModalityData?
    def _derive_data(self) -> ModalityData:
        """
        Derive data from another modality -- overridden by inheriting classes.

        This method should be implemented by subclasses by calling 
        a suitable deriving function to provide on-the-fly loading of data.

        This method is intended to rely on self.parent to provide the data
        to be processed.
        """
        raise NotImplementedError(
            "This method should be overridden by inheriting classes.")

    def _load_data(self) -> ModalityData:
        """
        Load data from a saved file -- to be overridden by inheriting classes.

        This method should be implemented by subclasses by calling 
        a suitable loading function to provide on-the-fly loading of data.

        This method is intended to rely on self.load_path to know what to read.
        """
        raise NotImplementedError(
            "This method should be overridden by inheriting classes.")

    def _read_data(self) -> ModalityData:
        """
        Load data from file -- to be overridden by inheriting classes.

        This method should be implemented by subclasses by calling 
        a suitable reading function to provide on-the-fly loading of data.

        This method is intended to rely on self.data_path to know what to read.
        """
        raise NotImplementedError(
            "This method should be overridden by inheriting classes.")

    def _set_data(self, data: ModalityData):
        """Set data from _get_data, _load_data, and _derive_data."""
        self._data = data.data
        self._timevector = data.timevector
        self._sampling_rate = data.sampling_rate

    @property
    def name(self) -> str:
        """
        Identity and possible parent data class.

        This will be just the class name if this is a data Modality instance.
        For derived Modalities the name will be of the form
        '[own class name] on [data modality class name]'.

        Subclasses may override this behaviour to, for example, include
        the metric used to generate the instance in the name.
        """
        name_string = self.__class__.__name__
        if self.metadata and self.metadata.parent_name:
            name_string = name_string + " on " + self.metadata.parent_name
        return name_string

    @property
    def data(self) -> np.ndarray:
        """
        Abstract property: a NumPy array. 

        The data refers to the actual data this modality represents
        and for DerivedModality it is the result of running the 
        modality's algorithm on the original data.

        The dimensions of the array are in the 
        order of [time, others]

        If this modality is not preloaded, accessing this property will
        cause data to be loaded on the fly _and_ saved in memory. To 
        release the memory, assign None to this Modality's data.
        """
        if self._data is None:
            _datastructures_logger.debug(
                "In Modality data getter. self._data was None.")
            self._set_data(self._get_data())
        return self._data

    @data.setter
    def data(self, data: np.ndarray) -> None:
        """
        Data setter method.

        Arguments: 
        data -- either None or a numpy.ndarray with same dtype, size, 
            and shape as self.data.

        Assigning anything but None or a numpy ndarray with matching dtype,
        size, and shape will raise a OverWriteError.

        If shape of the data were to change then also shape of the timevector
        should potentially change. Unlikely that we'd try to deal that in any
        other way but to create a new Modality or even Recording.
        """
        self._data_setter(data)

    def _data_setter(self, data: np.ndarray) -> None:
        """Set the data property from this class and subclasses."""
        if self.data is not None and data is not None:
            if (data.dtype == self._data.dtype and
                    data.size == self._data.size and
                    data.shape == self._data.shape):
                self._data = data
            else:
                raise OverWriteError(
                    "Trying to write over raw ultrasound data with a numpy " +
                    "array that has non-matching dtype, size, or shape.\n" +
                    " data.shape = " + str(data.shape) + "\n" +
                    " self.data.shape = " + str(self._data.shape) + ".")
        else:
            self._data = data

    @abc.abstractmethod
    def get_meta(self) -> dict:
        """Return this Modality's metadata as a dictionary."""

    @property
    def sampling_rate(self) -> float:
        """Sampling rate of this Modality in Hz."""
        if not self._sampling_rate:
            self._set_data(self._get_data())
        return self._sampling_rate

    @property
    def parent_name(self) -> str:
        """Name of the Modality this Modality was derived from, if any."""
        return self.metadata.parent_name

    @property
    def time_offset(self):
        """
        The time offset of this modality.

        Assigning a value to this property is implemented so that
        self._timevector[0] stays equal to self._timeOffset. 

        If shape of the timevector were to change then also shape of the data
        should change. Unlikely that we'd try to deal that in any other way but
        to create a new Modality or even Recording.
        """
        if not self._time_offset:
            self._set_data(self._get_data())
        return self._time_offset

    @property
    def time_precision(self) -> float:
        """
        Timevector precision: the maximum of absolute deviations.

        Essentially this means that we are guestimating the timevector to be no
        more precise than the largest deviation from the average timestep.
        """
        if not self._time_precision:
            differences = np.diff(self.timevector)
            average = np.average(differences)
            deviations = np.abs(differences - average)
            self._time_precision = np.max(deviations)
        return self._time_precision

    @time_offset.setter
    def time_offset(self, time_offset):
        self._time_offset = time_offset
        if self.timevector:
            self._timevector = (self.timevector +
                                (time_offset - self.timevector[0]))

    @property
    def timevector(self):
        """
        The timevector corresponding to self.data as a NumPy array. 

        If the data has not been previously loaded, accessing this 
        property will cause data to be loaded on the fly _and_ saved 
        in memory. To release the memory, assign None to this 
        Modality's data. If the data has been previously 
        loaded and after that released, the timevector still persists and  
        accessing it does not trigger a new loading operation.

        Assigning a value to this property is implemented so 
        that self._timevector[0] stays equal to self._timeOffset. 
        """
        if self._timevector is None:
            self._set_data(self._get_data())
        return self._timevector

    @timevector.setter
    def timevector(self, timevector):
        if self._timevector is None:
            raise OverWriteError(
                "Trying to overwrite the time vector when "
                "it has not yet been initialised."
            )
        elif timevector is None:
            raise NotImplementedError(
                "Trying to set timevector to None.\n" +
                "Freeing timevector memory is currently not implemented."
            )
        else:
            if (timevector.dtype == self._timevector.dtype and
                timevector.size == self._timevector.size and
                    timevector.shape == self._timevector.shape):
                self._timevector = timevector
                self.time_offset = timevector[0]
            else:
                raise OverWriteError(
                    "Trying to write over raw ultrasound data with a numpy " +
                    "array that has non-matching dtype, size, or shape.\n" +
                    " timevector.shape = " + str(timevector.shape) + "\n" +
                    " self.timevector.shape = "
                    + str(self._timevector.shape) + ".")

    @property
    def excluded(self) -> None:
        """
        Boolean property for excluding this Modality from processing.

        Setting this to True will result in the whole Recording being 
        excluded by setting self.parent.excluded = True.
        """
        # TODO: decide if this actually needs to exist and if so,
        # should the above doc string actaully be true?
        return self._excluded

    @excluded.setter
    def excluded(self, excluded):
        self._excluded = excluded

        if excluded:
            pass
            # TODO 1.O: find a workaround for self.parent not existing
            # currently self.parent.excluded = excluded

    @property
    def is_derived_modality(self) -> bool:
        """
        Is this Modality a result of processing another.

        This cannot be set from the outside.
        """
        if self.metadata and self.metadata.parent_name:
            return True
        else:
            return False

    @property
    def meta_path(self) -> Path:
        """
        Path to meta data file if any, None otherwise.

        Only external data might have per Modality meta files before being
        first saved by SATKIT.
        """
        if not self._meta_path:
            path = Path(self.recording.basename).with_suffix(
                "." + self.name.replace(" ", "_"))
            path.with_suffix(SatkitSuffix.META)
        return self._meta_path


def satkit_suffix(
        satkit_type: Union[Recording, RecordingSession, Modality]) -> str:
    """
    Generate a suffix for the savefile of a SATKIT datastructure.

    Parameters
    ----------
    satkit_type : Union[Recording, RecordingSession, Modality]
        The datastructures type.

    Returns
    -------
    str
        The suffix.
    """
    # TODO 1.1: This is one possibility for not having hardcoded file suffixes.
    # Another is to let all the classes take care of it themselves and make it
    # into a Protocol (Python version of an interface).
    suffix = SatkitSuffix.META
    if satkit_type == Recording:
        suffix = '.Recording' + suffix
    elif satkit_type == RecordingSession:
        suffix = '.RecordingSession' + suffix
    elif satkit_type == Modality:
        suffix = ''
    return suffix
