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
SatGrid and its components are a GUI friendly encapsulation of
`textgrids.TextGrid`.
"""

from collections import OrderedDict
from typing import Optional, Union

from icecream import ic

from textgrids import Interval, TextGrid, Tier, Transcript
from textgrids.templates import (long_header, long_interval, long_point,
                                 long_tier)
from typing_extensions import Self

from satkit.configuration import config_dict
from satkit.constants import IntervalCategory


class SatInterval:
    """TextGrid Interval representation to enable editing with GUI."""

    @classmethod
    def from_textgrid_interval(
        cls,
        interval: Interval,
        prev: Union[None, Self],
        next_interval: Union[None, Self] = None
    ) -> Self:
        """
        Copy the info of a Python TextGrids Interval into a new SatInterval.

        Only xmin and text are copied from the original Interval. xmax is
        assumed to be handled by either the next SatInterval or the
        constructing method if this is the last Interval. 

        Since SatIntervals are doubly linked, an attempt will be made to link
        prev and next to this interval. 

        Returns the newly created SatInterval.
        """
        return cls(
            begin=interval.xmin,
            text=interval.text,
            prev=prev,
            next_interval=next_interval)

    def __init__(self,
                 begin: float,
                 text: Union[None, Transcript],
                 prev: Union[None, Self] = None,
                 next_interval: Union[None, Self] = None) -> None:
        self.begin = begin
        self.text = text

        self.prev = prev
        if self.prev:
            self.prev.next_interval = self

        self.next_interval = next_interval
        if self.next_interval:
            self.next_interval.prev = self

    @property
    def mid(self) -> Union[float, None]:
        """
        Middle time point of the interval.

        This is a property that will return None
        if this Interval is the one that marks
        the last boundary.
        """
        if self.next_interval:
            return (self.begin+self.next_interval.begin)/2
        return None

    @property
    def end(self) -> Union[float, None]:
        """
        End time point of the interval.

        This is a property that will return None
        if this Interval is the one that marks
        the last boundary.
        """
        if self.next_interval:
            return self.next_interval.begin
        return None

    def is_legal_value(self, time: float) -> bool:
        """
        Check if the given time is between the previous and next boundary.

        Usual caveats about float testing don't apply, because each boundary is
        padded with SATKIT epsilon. Tests used do not include equality with
        either bounding boundary, and that may or may not be trusted to be the
        actual case depending on how small the epsilon is.

        Returns True, if time is  between the previous and next boundary.
        """
        return (time + config_dict['epsilon'] < self.next_interval.begin and
                time > config_dict['epsilon'] + self.prev.begin)

    def is_at_time(self, time):
        """
        Intervals are considered equivalent if the difference between their
        begin values is < epsilon. Epsilon is a constant defined in SATKIT's
        configuration.
        """
        return abs(self.begin - time) < config_dict['epsilon']

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}: text: '{self.text}'\t "
                f"begin: {self.begin}, end: {self.end}")


class SatTier(list):
    """TextGrid Tier representation to enable editing with GUI."""

    @classmethod
    def from_textgrid_tier(cls, tier: Tier) -> Self:
        """
        Copy a Python TextGrids Tier as a SatTier.

        Returns the newly created SatTier.
        """
        return cls(tier)

    def __init__(self, tier: Tier) -> None:
        last_interval = None
        prev = current = None
        for interval in tier:
            current = SatInterval.from_textgrid_interval(interval, prev)
            self.append(current)
            prev = current
            last_interval = interval
        self.append(SatInterval(last_interval.xmax, None, prev))

    @property
    def begin(self) -> float:
        """
        Begin timestamp.

        Corresponds to a TextGrid Interval's xmin.

        This is a property and the actual value is generated from the first
        SatInterval of this SatTier.
        """
        return self[0].begin

    @property
    def end(self) -> float:
        """
        End timestamp.

        Corresponds to a TextGrid Interval's xmin.

        This is a property and the actual value is generated from the last
        SatInterval of this SatTier.
        """
        # This is slightly counter intuitive, but the last interval is in fact
        # empty and only represents the final boundary. So its begin is the
        # final boundary.
        return self[-1].begin

    @property
    def is_point_tier(self) -> bool:
        """Is this Tier a PointTier."""
        return False

    def __repr__(self) -> str:
        representation = f"{self.__class__.__name__}:\n"
        for interval in self:
            representation += str(interval) + "\n"
        return representation

    def boundary_at_time(self, time) -> Union[SatInterval, None]:
        """
        If there is a boundary at time, return it.

        Returns None, if there is no boundary at time. 

        'Being at time' is defined as being within SATKIT epsilon of the given
        timestamp.
        """
        for interval in self:
            if interval.is_at_time(time):
                return interval
        return None

    def get_interval_by_category(
        self,
        interval_category: IntervalCategory,
        label: Optional[str] = None
    ) -> SatInterval:
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
        SatInterval
            _description_
        """
        if interval_category is IntervalCategory.FIRST_NON_EMPTY:
            for interval in self:
                if interval.text:
                    return interval

        if interval_category is IntervalCategory.LAST_NON_EMPTY:
            for interval in reversed(self):
                if interval.text:
                    return interval

        if interval_category is IntervalCategory.FIRST_LABELED:
            for interval in self:
                ic(label)
                if interval.text == label:
                    return interval

        if interval_category is IntervalCategory.LAST_LABELED:
            for interval in reversed(self):
                if interval.text == label:
                    return interval


class SatGrid(OrderedDict):
    """
    TextGrid representation which makes editing easier.

    SatGrid is a OrderedDict very similar to Python textgrids TextGrid, but
    made up of SatTiers that in turn contain intervals or points as doubly
    linked lists instead of just lists. See the relevant classes for more
    details.
    """

    def __init__(self, textgrid: TextGrid) -> None:
        for tier_name in textgrid:
            self[tier_name] = SatTier.from_textgrid_tier(textgrid[tier_name])

    # def as_textgrid(self):
    #     pass

    @property
    def begin(self) -> float:
        """
        Begin timestamp.

        Corresponds to a TextGrids xmin.

        This is a property and the actual value is generated from the first
        SatTier of this SatGrid.
        """
        key = list(self.keys())[0]
        return self[key].begin

    @property
    def end(self) -> float:
        """
        End timestamp.

        Corresponds to a TextGrids xmax.

        This is a property and the actual value is generated from the first
        SatTier of this SatGrid.
        """
        # First Tier
        key = list(self.keys())[0]
        # Return the end of the first Tier.
        return self[key].end

    def format_long(self) -> str:
        '''Format self as long format TextGrid.'''
        out = long_header.format(self.begin, self.end, len(self))
        tier_count = 1
        for name, tier in self.items():
            if tier.is_point_tier:
                tier_type = 'PointTier'
                elem_type = 'points'
            else:
                tier_type = 'IntervalTier'
                elem_type = 'intervals'
            out += long_tier.format(tier_count,
                                    tier_type,
                                    name,
                                    self.begin,
                                    self.end,
                                    elem_type,
                                    len(tier)-1)
            for elem_count, elem in enumerate(tier, 1):
                if tier.is_point_tier:
                    out += long_point.format(elem_count,
                                             elem.xpos,
                                             elem.text)
                elif elem.next:
                    out += long_interval.format(elem_count,
                                                elem.begin,
                                                elem.next.begin,
                                                elem.text)
                else:
                    # The last interval does not contain anything.
                    # It only marks the end of the file and final
                    # interval's end. That info got already used by
                    # elem.next.begin above.
                    pass
        return out
