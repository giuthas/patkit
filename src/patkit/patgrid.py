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
PatGrid and its components are a GUI friendly encapsulation of
`textgrids.TextGrid`.
"""
from abc import ABC, abstractmethod
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path

import numpy as np
from textgrids import Interval, Point, TextGrid, Tier, Transcript
from textgrids.templates import (long_header, long_interval, long_point,
                                 long_tier)
from typing_extensions import Self

from patkit.constants import IntervalCategory, PATKIT_EPSILON

# TODO 0.24: clean up the way epsilon is used and how it's type hinted and
# documented.


class PatAnnotation(ABC):
    """
    Base class for Textgrid Point and Interval to enable editing with GUI.
    """

    def __init__(
            self,
            time: float,
            label: None | Transcript,
    ) -> None:
        self._time = time
        self.label = label

    @property
    def time(self) -> float:
        """Location of this Point."""
        return self._time

    @time.setter
    def time(self, time: float) -> None:
        self._time = time

    @abstractmethod
    def contains(self, time: float, epsilon: float | None) -> bool:
        """
        Does this Interval contain `time` or is this Point at `time`.

        'Being at time' is defined in the sense of 'within epsilon of time'.

        Parameters
        ----------
        time : float
            The time in seconds to test against this Annotation.
        epsilon : float | None
            The precision (in seconds) to use in comparisons. The default value
            None will result in PATKIT_EPSILON, being used. For expected
            behaviour, `configuration.data_config.epsilon` should be passed
            here.

        Returns
        -------
        bool
            True if `time` is in this Interval or at this Point.
        """


class PatPoint(PatAnnotation):
    """TextGrid Point representation to enable editing with GUI."""

    @classmethod
    def from_textgrid_point(
            cls,
            point: Point,
    ) -> Self:
        """
        Copy the info of a Python TextGrids Interval into a new PatInterval.

        Only xmin and text are copied from the original Interval. xmax is
        assumed to be handled by either the next PatInterval or the
        constructing method if this is the last Interval.

        Since PatIntervals are doubly linked, an attempt will be made to link
        prev and next to this interval.

        Returns the newly created PatInterval.
        """
        return cls(
            time=point.xpos,
            label=point.text,
        )

    def __init__(
            self,
            time: float,
            label: None | Transcript
    ) -> None:
        super().__init__(time=time, label=label)

    def contains(self, time: float, epsilon: float | None) -> bool:
        if epsilon is None:
            epsilon = PATKIT_EPSILON
        if self._time - epsilon < time < self._time + epsilon:
            return True
        return False


class PatInterval(PatAnnotation):
    """TextGrid Interval representation to enable editing with GUI."""

    @classmethod
    def from_textgrid_interval(
        cls,
        interval: Interval,
        prev_interval: None | Self,
        next_interval: None | Self = None
    ) -> Self:
        """
        Copy the info of a Python TextGrids Interval into a new PatInterval.

        Only xmin and text are copied from the original Interval. xmax is
        assumed to be handled by either the next PatInterval or the
        constructing method if this is the last Interval.

        Since PatIntervals are doubly linked, an attempt will be made to link
        prev and next to this interval.

        Returns the newly created PatInterval.
        """
        return cls(
            begin=interval.xmin,
            label=interval.text,
            prev_interval=prev_interval,
            next_interval=next_interval)

    def __init__(self,
                 begin: float,
                 label: None | Transcript,
                 prev_interval: None | Self = None,
                 next_interval: None | Self = None) -> None:
        super().__init__(
            time=begin,
            label=label,
        )

        self._prev_interval = prev_interval
        if self.prev:
            self.prev._next_interval = self

        self._next_interval = next_interval
        if self.next:
            self.next.prev = self

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}: text: '{self.label}'\t "
                f"begin: {self.begin}, end: {self.end}")

    @property
    def next(self) -> Self | None:
        """The next annotation, if any."""
        return self._next_interval

    @next.setter
    def next(self, next_interval: Self | None) -> None:
        if next_interval != self._next_interval:
            self._next_interval = next_interval

    @property
    def prev(self) -> Self | None:
        """The previous annotation, if any."""
        return self._prev_interval

    @prev.setter
    def prev(self, prev_interval: Self | None) -> None:
        if prev_interval != self._prev_interval:
            self._prev_interval = prev_interval

    @property
    def begin(self) -> float:
        """Beginning time point of the interval."""
        return self._time

    @begin.setter
    def begin(self, value: float) -> None:
        self._time = value

    @property
    def mid(self) -> float | None:
        """
        Middle time point of the interval.

        This is a property that will return None
        if this Interval is the one that marks
        the last boundary.
        """
        if self._next_interval:
            return (self.begin + self._next_interval.begin)/2
        return None

    @property
    def end(self) -> float | None:
        """
        End time point of the interval.

        This is a property that will return None
        if this Interval is the one that marks
        the last boundary.
        """
        if self._next_interval:
            return self._next_interval.begin
        return None

    @end.setter
    def end(self, value: float) -> None:
        if self._next_interval:
            self._next_interval.begin = value

    def is_at_time(self, time: float, epsilon) -> bool:
        """
        Intervals are considered equivalent if the difference between their
        `begin` values is < epsilon. Epsilon is a constant defined in patkit's
        configuration.
        """
        return abs(self.begin - time) < epsilon

    def is_last(self) -> bool:
        """Is this the last Interval in this Tier."""
        return self._next_interval is None

    def is_legal_value(self, time: float, epsilon: float) -> bool:
        """
        Check if the given time is between the previous and next boundary.

        Usual caveats about float testing don't apply, because each boundary is
        padded with patkit epsilon. Tests used do not include equality with
        either bounding boundary, and that may or may not be trusted to be the
        actual case depending on how small the epsilon is.

        Returns True, if time is  between the previous and next boundary.
        """
        return (time + epsilon < self._next_interval.begin and
                time > epsilon + self.prev.begin)

    def contains(self, time: float, epsilon: float | None) -> bool:
        if self.begin < time < self.end:
            return True
        return False


class PatTier(list):
    """TextGrid Tier representation to enable editing with GUI."""

    @classmethod
    def from_textgrid_tier(cls, tier: Tier) -> Self:
        """
        Copy a Python TextGrids Tier as a PatTier.

        Returns the newly created PatTier.
        """
        return cls(tier)

    def __init__(self, tier: Tier) -> None:
        super().__init__()
        last_interval = None
        prev = None
        for interval in tier:
            current = PatInterval.from_textgrid_interval(interval, prev)
            self.append(current)
            prev = current
            last_interval = interval
        self.append(PatInterval(last_interval.xmax, None, prev))

    def __repr__(self) -> str:
        representation = f"{self.__class__.__name__}:\n"
        for interval in self:
            representation += str(interval) + "\n"
        return representation

    @property
    def begin(self) -> float:
        """
        Begin timestamp.

        Corresponds to a TextGrid Interval's xmin.

        This is a property and the actual value is generated from the first
        PatInterval of this PatTier.
        """
        return self[0].begin

    @property
    def end(self) -> float:
        """
        End timestamp.

        Corresponds to a TextGrid Interval's xmin.

        This is a property and the actual value is generated from the last
        PatInterval of this PatTier.
        """
        # This is slightly counterintuitive, but the last interval is in fact
        # empty and only represents the final boundary. So its `begin` is the
        # final boundary.
        return self[-1].begin

    @property
    def is_point_tier(self) -> bool:
        """Is this Tier a PointTier."""
        return False

    def boundary_at_time(
            self, time: float, epsilon: float) -> PatInterval | None:
        """
        If there is a boundary at time, return it.

        Returns None, if there is no boundary at time.

        'Being at time' is defined as being within patkit epsilon of the given
        timestamp.
        """
        for interval in self:
            if interval.is_at_time(time=time, epsilon=epsilon):
                return interval
        return None

    def get_interval_by_category(
        self,
        interval_category: IntervalCategory,
        label: str | None = None
    ) -> PatInterval:
        """
        Return the Interval matching the category in this Tier.

        If interval_category is FIRST_LABELED or LAST_LABELED, the label should
        be specified as well.

        Parameters
        ----------
        interval_category : IntervalCategory
            The category to search for.
        label : Optional[str], optional
            Label to search for when doing a label based category search, by
            default None

        Returns
        -------
        PatInterval
            The matching PatInterval
        """
        if interval_category is IntervalCategory.FIRST_NON_EMPTY:
            for interval in self:
                if interval.label:
                    return interval

        if interval_category is IntervalCategory.LAST_NON_EMPTY:
            for interval in reversed(self):
                if interval.label:
                    return interval

        if interval_category is IntervalCategory.FIRST_LABELED:
            for interval in self:
                if interval.label == label:
                    return interval

        if interval_category is IntervalCategory.LAST_LABELED:
            for interval in reversed(self):
                if interval.label == label:
                    return interval

    def get_labels(
            self, time_vector: np.ndarray, epsilon: float | None = None,
    ) -> np.ndarray:
        """
        Get the labels at the times in the `time_vector`.

        Parameters
        ----------
        time_vector : np.ndarray
            Time stamps to retrieve the labels for.
        epsilon : float | None
            The precision (in seconds) to use in comparisons. The default value
            None will result in PATKIT_EPSILON, being used. For expected
            behaviour for `PointTiers`, `configuration.data_config.epsilon`
            should be passed here.

        Returns
        -------
        np.ndarray
            This array contains the labels as little endian Unicode strings.
        """
        max_label = max(
            [len(element.label) for element in self
             if element.label is not None]
        )
        labels = np.empty(len(time_vector), dtype=f"<U{max_label}")
        for (i, time) in enumerate(time_vector):
            labels[i] = self.label_at(time, epsilon)
        return labels

    def label_at(self, time: float, epsilon: float | None = None) -> str:
        """
        Get the label at the given time.

        Parameters
        ----------
        time : float
            Time in seconds to retrieve the label for.
        epsilon : float | None
            The precision (in seconds) to use in comparisons. The default value
            None will result in PATKIT_EPSILON, being used. For expected
            behaviour for `PointTiers`, `configuration.data_config.epsilon`
            should be passed here.

        Returns
        -------
        str
            The label string.
        """
        if time < self.begin or time > self.end:
            return ""

        for element in self:
            if element.contains(time=time, epsilon=epsilon):
                return element.label

    def intersects(self, xlim: list[float, float]) -> list[PatAnnotation]:
        """
        List the items that intersect with the given time interval.

        Parameters
        ----------
        xlim : list[float, float]
            The time interval in seconds.

        Returns
        -------
        list[PatAnnotation]
            List of PatAnnotations that intersect with the interval.
        """
        in_limits = []
        if len(self) > 0:
            if isinstance(self[0], PatInterval):
                for item in self:
                    if item.end is None:
                        if xlim[1] < item.begin:
                            continue
                        if item.begin < xlim[0]:
                            continue
                    elif item.end < xlim[0] or xlim[1] < item.begin:
                        continue
                    in_limits.append(item)
            else:
                for item in self:
                    if item.time < xlim[1] and xlim[0] < item.time:
                        in_limits.append(item)

        return in_limits

    def scramble(self):
        boundaries = np.linspace(
            start=self.begin,
            stop=self.end,
            num=len(self)
        )
        for item, boundary in zip(self, boundaries):
            item.time = boundary


class PatGrid(OrderedDict):
    """
    TextGrid representation which makes editing easier.

    PatGrid is a OrderedDict very similar to Python textgrids TextGrid, but
    made up of PatTiers that in turn contain intervals or points as doubly
    linked lists instead of just lists. See the relevant classes for more
    details.
    """

    def __init__(self, textgrid: TextGrid | Path | str) -> None:
        """
        Initialize a PatGrid.

        Parameters
        ----------
        textgrid : TextGrid | Path | str
            An already parsed textgrids.TextGrid object, or a path to a 
            TextGrid file on disk.
        """
        super().__init__()

        if isinstance(textgrid, (Path, str)):
            textgrid = TextGrid(textgrid)

        for tier_name in textgrid:
            self[tier_name] = PatTier.from_textgrid_tier(textgrid[tier_name])

    # def as_textgrid(self):
    #     pass

    def __deepcopy__(self, memo):
        cls = self.__class__
        new_copy = cls.__new__(cls)
        memo[id(self)] = new_copy
        for tier_name, tier in self.items():
            new_copy[tier_name] = deepcopy(tier)
        return new_copy

    def __repr__(self):
        representation = "PatGrid:"
        for tier_name in self:
            representation += f"\n\tTier: {tier_name}"
            for item in self[tier_name]:
                if isinstance(item, PatInterval):
                    representation += f"\n\t\t{item}"
        return representation

    @property
    def begin(self) -> float:
        """
        Begin timestamp.

        Corresponds to a TextGrids xmin.

        This is a property and the actual value is generated from the first
        PatTier of this PatGrid.
        """
        key = list(self.keys())[0]
        return self[key].begin

    @property
    def end(self) -> float:
        """
        End timestamp.

        Corresponds to a TextGrids xmax.

        This is a property and the actual value is generated from the first
        PatTier of this PatGrid.
        """
        # First Tier
        key = list(self.keys())[0]
        # Return the end of the first Tier.
        return self[key].end

    def format_long(self) -> str:
        """Format self as long format TextGrid."""
        out = long_header.format(self.begin, self.end, len(self))
        tier_count = 1
        for name, tier in self.items():
            if tier.is_point_tier:
                tier_type = 'PointTier'
                element_type = 'points'
            else:
                tier_type = 'IntervalTier'
                element_type = 'intervals'
            out += long_tier.format(tier_count,
                                    tier_type,
                                    name,
                                    self.begin,
                                    self.end,
                                    element_type,
                                    len(tier)-1)
            for element_count, element in enumerate(tier, 1):
                if tier.is_point_tier:
                    out += long_point.format(element_count,
                                             element.time,
                                             element.label)
                elif element.next:
                    out += long_interval.format(element_count,
                                                element.begin,
                                                element.end,
                                                element.label)
                else:
                    # The last interval does not contain anything. It only
                    # marks the end of the file and final interval's end. That
                    # info got already used by element.end (which is
                    # element.next.begin) above.
                    pass
        return out

    def get_labels(
            self, time_vector: np.ndarray, epsilon: float | None = None
    ) -> dict[str, np.ndarray]:
        """
        Get the labels at the times in the `time_vector`.

        Parameters
        ----------
        time_vector : np.ndarray
            Time values to get the labels for.
        epsilon : float | None
            The precision (in seconds) to use in comparisons. The default value
            None will result in PATKIT_EPSILON, being used. For expected
            behaviour for `PointTiers`, `configuration.data_config.epsilon`
            should be passed here.

        Returns
        -------
        dict[str, np.ndarray]
            Dictionary of the labels indexed by tier name.
        """
        labels = {}
        for tier_name in self:
            labels[tier_name] = self[tier_name].get_labels(
                time_vector, epsilon=epsilon)

        return labels
