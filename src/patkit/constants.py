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
This module contains all sorts of constants used by patkit.

Enums are used for constants that need to be instantiated from other variables.
They maybe used as fields in other objects. Using an Enum limits the possible
values and avoids typos and makes an IDE help in writing code.

Frozen dataclasses are used for constants that only ever need to be accessed
and never are stored. In effect, they function as look-up tables.
"""
from enum import Enum
from importlib.metadata import version

from patkit.external_class_extensions import (
    enum_union, ListablePrintableEnum, ValueComparedEnumMeta
)

# TODO 1.0: Decouple program and file format versions at version 1.0.
PATKIT_VERSION = version('patkit')
PATKIT_FILE_VERSION = PATKIT_VERSION
EXERCISE_FILE_VERSION = PATKIT_VERSION

DEFAULT_ENCODING = 'utf-8'

PATKIT_CONFIG_DIR = "~/.patkit/"
PATKIT_HISTORY_FILE = PATKIT_CONFIG_DIR + "history"

# TODO 0.24 still not happy with this and how it meshes with patgrid.
PATKIT_EPSILON = 0.00001


class AaaProbeType(Enum):
    """
    Probe type codes saved by AAA.

    These are probe models, not 'fan' vs 'linear' or some such thing.
    """
    UNKNOWN = -1
    ZERO = 0
    ONE = 1


class AnnotationType(Enum):
    """
    Enum to differentiate Modality annotation types
    """
    PEAKS = "peaks"
    ARTICULATORY_ONSET = "articulatory_onset"
    ACOUSTIC_ONSET = "acoustic_onset"


class ComparisonMember(ListablePrintableEnum):
    """
    Which comparison member the perturbations should be applied to.
    """
    FIRST = "first"
    SECOND = "second"


class CoordinateSystems(Enum):
    """
    Enum to differentiate coordinate systems.
    """
    CARTESIAN = 'Cartesian'
    POLAR = 'polar'


class DatasourceNames(Enum):
    """
    Names of data sources PATKIT can handle.

    Used in saving and loading to identify the data source in config, as well
    as in meta. Used to skip the step of trying to figure the data source out
    from the type of files present.
    """
    AAA = "AAA"
    # EVA = "EVA"
    RASL = "RASL"
    WAV = "WAV"


class GuiColorScheme(Enum):
    """
    GUI styles.

    FOLLOW_SYSTEM means patkit will try to follow the dark/light theme setting
    the system uses.
    """
    DARK = "dark"
    FOLLOW_SYSTEM = "follow_system"
    LIGHT = "light"


class GuiImageType(Enum):
    """
    GUI image types for specifying the type of image to be shown in a panel.
    """
    MEAN_IMAGE = "mean_image"
    FRAME = "frame"
    RAW_FRAME = "raw_frame"


class AxesType(Enum):
    """
    Axes types in plotting.
    """
    DATA = 'data_axes'
    TIER = 'tier_axes'


class ImageMask(Enum):
    """
    Accepted image masking options in calculating PD.
    """
    TOP = "top"
    BOTTOM = "bottom"
    WHOLE = "whole"

    def __str__(self):
        return self.value


class IntervalBoundary(Enum):
    """
    Begin and end for import type checking.
    """
    BEGIN = 'begin'
    END = 'end'


class IntervalCategory(Enum):
    """
    Rule-based interval selection categories for import type checking.
    """
    FIRST_NON_EMPTY = 'first non-empty'
    LAST_NON_EMPTY = 'last non-empty'
    FIRST_LABELED = 'first labeled'
    LAST_LABELED = 'last labeled'


class PatkitConfigFile(str, Enum):
    """
    Human written yaml files to control importing data.

    Please note, that while MAIN corresponds to `patkit.yaml` which is the
    conventional name for the file containing paths/names of other config files
    such as data, gui, publish, and simulation config, and those files have
    conventional names (`patkit_data.yaml` etc.), these filenames are only a
    convention. The MAIN here is more of a guess of what we should look for
    than a hard rule, and the rest should be specified in `patkit.yaml` instead
    of PATKIT trying to guess their names.

    DATA: specifications for processing data and deriving new Modalities and
        Statistics.
    GUI: specifications for gui elements - which graphs to display, color
        scheme etc.
    PUBLISH: specifications for publishing graphs
    SIMULATION: specifications for simulating data and running analysis on the
        simulated data
    MANIFEST: list of Scenarios relating to a set of recorded data saved with
        recorded data
    SESSION: how PATKIT should read a session based on recorded data
    SPLINE: spline formatting
    """
    ANSWER = "patkit-answer.yaml"
    EXERCISE = "patkit-exercise.yaml"
    DATA = "patkit-data.yaml"
    GUI = "patkit-gui.yaml"
    PUBLISH = "patkit-publish.yaml"
    SIMULATION = "patkit-simulation.yaml"
    MANIFEST = "patkit-manifest.yaml"
    SESSION = 'session-config.yaml'
    SPLINE = 'spline-config.yaml'

    def __str__(self) -> str:
        """
        Ensure f-strings and print() output the string value.
        """
        return self.value


class PatkitDirectory(str, Enum):
    """
    Standard directory names used in PATKIT.
    """
    ANSWERS = "answers"
    EXAMPLE = "example"

    def __str__(self) -> str:
        """
        Ensure f-strings and print() output the string value.
        """
        return self.value


class PatkitSuffix(str, Enum):
    """
    Suffixes for files saved by patkit.

    These exist as a convenient way of not needing to risk typos. To see the
    whole layered scheme patkit uses see the 'Saving and Loading Data' section
    in the documentation.
    """
    CONFIG = ".yaml"
    DATA = ".npz"
    META = ".meta"

    def __str__(self) -> str:
        """
        Ensure f-strings and print() output the string value.
        """
        return self.value


class SavedObjectTypes(Enum):
    """
    Represent type of a saved patkit object in .meta.
    """
    EXERCISE = "Exercise"
    DATASET = "Dataset"
    MODALITY = "Modality"
    RECORDING = "Recording"
    SESSION = "Session"
    SOURCE = "Source"
    STATISTIC = "Statistic"
    TRIAL = "Trial"


class SourceSuffix(str, Enum):
    """
    Suffixes for files imported by patkit.

    These exist as a convenient way of not needing to risk typos and for
    recognising what patkit is being asked to import.

    Note that AAA_ULTRA_META_OLD is not a proper suffix and won't be recognised
    by pathlib and Path as such. Instead, do this
    ```python
    directory_path = Path(from_some_source)
    directory_path/(name_string + SourceSuffix.AAA_ULTRA_META_OLD)
    ```
    """
    AAA_ULTRA = ".ult"
    AAA_ULTRA_META_OLD = "US.txt"
    AAA_ULTRA_META_NEW = ".param"
    AAA_PROMPT = ".txt"
    AAA_SPLINES = ".spl"
    AVI = ".avi"
    CSV = ".csv"
    TEXTGRID = ".TextGrid"
    WAV = ".wav"

    def __str__(self) -> str:
        """
        Ensure f-strings and print() output the string value.
        """
        return self.value


class OpenPathType(Enum):
    """
    Path types resolved when running patkit subcommands (open, interact...).
    """
    MANIFEST = "manifest"
    SCENARIO = "scenario"
    SINGLE_DATA = "single_data"
    DIRECTORY = "directory"


# def patkit_suffix(
#         patkit_type: Union[Recording, Session, Modality]) -> str:
#     """
#     Generate a suffix for the save file of a patkit data structure.

#     Parameters
#     ----------
#     patkit_type : Union[Recording, Session, Modality]
#         The datastructures type.

#     Returns
#     -------
#     str
#         The suffix.
#     """
#     # TODO 1.1: This is one possibility for not having hardcoded file
#     # suffixes.
#     # Another is to let all the classes take care of it themselves
#     # and make it into a Protocol (Python version of an interface).
#     suffix = patkitSuffix.META
#     if patkit_type == Recording:
#         suffix = '.Recording' + suffix
#     elif patkit_type == Session:
#         suffix = '.Session' + suffix
#     elif patkit_type == Modality:
#         suffix = ''
#     return suffix


class SplineDataColumn(Enum):
    """
    Basic data columns that any Spline should reasonably have.

    Accepted values: 'r' with 'phi', 'x' with 'y', and 'confidence'
    """
    R = "r"
    PHI = "phi"
    X = "x"
    Y = "y"
    CONFIDENCE = "confidence"


class SplineMetaColumn(Enum):
    """
    Basic metadata that any Spline should reasonably have.

    Accepted values:
    - ignore: marks a column to be ignored, unlike the others below,
        can be used several times
    - id: used to identify the speaker,
        often contained in a csv field called 'family name'
    - given names: appended to 'id' if not marked 'ignore'
    - date and time: dat3 and time of recording
    - prompt: prompt of recording, used to identify the recording with 'id'
    - annotation label: optional field containing annotation information
    - time in recording: timestamp of the frame this spline belongs to
    - number of spline points: number of sample points in the spline used
        to parse the coordinates and possible confidence information
    """
    IGNORE = "ignore"
    ID = "id"
    GIVEN_NAMES = "given names"
    DATE_AND_TIME = "date and time"
    PROMPT = "prompt"
    ANNOTATION_LABEL = "annotation label"
    TIME_IN_RECORDING = "time in recording"
    NUMBER_OF_SPLINE_POINTS = "number of spline points"


class SplineDiffsEnum(ListablePrintableEnum, metaclass=ValueComparedEnumMeta):
    """
    Spline metrics that use distance between corresponding points.
    """
    APBPD = 'apbpd'
    MPBPD = 'mpbpd'
    SPLINE_L1 = 'spline_l1'
    SPLINE_L2 = 'spline_l2'


class SplineNNDsEnum(ListablePrintableEnum, metaclass=ValueComparedEnumMeta):
    """
    Spline metrics that use nearest neighbour distance.
    """
    ANND = 'annd'
    MNND = 'mnnd'


class SplineShapesEnum(ListablePrintableEnum, metaclass=ValueComparedEnumMeta):
    """
    Spline metrics that characterise shape.
    """
    CURVATURE = 'curvature'
    FOURIER = 'fourier'
    MODIFIED_CURVATURE = 'modified_curvature'
    PROCRUSTES = 'procrustes'

    def short_name(self) -> str:
        """
        Return the short name or abbreviation of this SplineShape metric.

        Returns
        -------
        str
            The short name.
        """
        match self:
            case SplineShapesEnum.CURVATURE:
                return "CI"
            case SplineShapesEnum.FOURIER:
                return "Fourier"
            case SplineShapesEnum.MODIFIED_CURVATURE:
                return "MCI"
            case SplineShapesEnum.PROCRUSTES:
                return "PROC"


SplineMetricEnum = enum_union(
    [SplineDiffsEnum, SplineNNDsEnum, SplineShapesEnum], "SplineMetricEnum")
"""
Enum of all valid spline metrics.

This is formed as a UnionEnum of the subtypes.
"""


class SimulationContourVowel(
        ListablePrintableEnum, metaclass=ValueComparedEnumMeta):
    """
    Currently available simulated vowel contours.
    """
    AE = 'æ'
    I = 'i'


class SimulationContourConsonant(
        ListablePrintableEnum, metaclass=ValueComparedEnumMeta):
    """
    Currently available simulated consonant contours.

    Yes, at the moment there are none.
    """


SimulationContourSoundEnum = enum_union(
    [SimulationContourVowel, SimulationContourConsonant],
    "SimulationContourEnum")


class OverwriteConfirmation(Enum):
    """
    Codes for a user's response when asked if a file should be overwritten.
    """
    YES = 'yes'
    YES_TO_ALL = 'yes to all'
    NO = 'no'
    NO_TO_ALL = 'no to all'


class AnnotatorMode(ListablePrintableEnum, metaclass=ValueComparedEnumMeta):
    """
    Modes of the PATKIT Annotator.
    """
    ANALYSE = "Analyse"
    EXERCISE = "Exercise"


class ExerciseMode(ListablePrintableEnum, metaclass=ValueComparedEnumMeta):
    """
    Modes of the PATKIT Annotator Exercises.
    """
    ANSWER = "Answer"
    EXAMPLE = "Example"
