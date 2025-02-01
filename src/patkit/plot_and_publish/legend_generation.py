#
# Copyright (c) 2019-2025
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
Generate legend labels for plotting.
"""
from difflib import get_close_matches

from patkit.data_structures import Modality
from patkit.utility_functions import split_by


def process_format_directive(
        modality: Modality,
        directive: str,
        index: int
) -> str:
    """
    Process a string formatting directive based on a Modality.

    Fills the string with requested information form this Modality.

    Parameters
    ----------
    modality : Modality
        The Modality to draw the (meta)data from.
    directive : str
        The directive in the format "[field_name]:[format]" where field_name
        is an accepted field name either from this Modality or its
        metadata.
    index : int
        Index within the legend being created. Currently discarded.

    Returns
    -------
    str
        The filled and formatted string.
    """
    if ":" in directive:
        field_name, format_specifier = directive.split(sep=":", maxsplit=1)
    else:
        field_name = directive
        format_specifier = None

    if field_name == "sampling_rate":
        if format_specifier is not None:
            return format(modality.sampling_rate, format_specifier)
        return str(modality.sampling_rate)
    elif field_name in modality.metadata.__dict__:
        if format_specifier is not None:
            return format(
                modality.metadata.__dict__[field_name], format_specifier)
        return str(modality.metadata.__dict__[field_name])
    else:
        _logger.error(
            "Field name '%s' not found in metadata of %s.",
            field_name, modality.name)
        _logger.error(
            "Valid names are\n'%s', and 'sampling_rate'.",
            str("', '".join(list(modality.metadata.__dict__.keys()))))
        _logger.error(
            "Did you mean '%s'?",
            "', '".join(get_close_matches(field_name,
                                          modality.metadata.__dict__.keys()))
        )
        # DO NOT add the field_name to the below. It is a variable read from
        # a file and using it in an f-string is a very serious security
        # risk.
        raise ValueError(
            f"Missing field name in {modality.name} and its metadata.",
        )


def format_legend(
        modality: Modality,
        index: int,
        format_strings: list[str] | None,
        delimiters: str = "{}"
) -> str:
    """
    Fill and format a legend string from a Modality.

    If the format_strings are None, then we return the name of this
    Modality.

    Parameters
    ----------
    modality : Modality
        The Modality to draw the (meta)data from.
    index : int
        Index within the legend being created. Currently discarded.
    format_strings : list[str]
        The combined format strings for the whole plot, possibly None.
    delimiters :
        The delimiter character(s) for the fields.

    Returns
    -------
    str
        The filled and formatted legend string.
    """
    if format_strings is None:
        return modality.name

    result = ""
    format_string = format_strings[index]
    for chunk, is_directive in split_by(format_string, delimiters):
        if not is_directive:
            result += chunk
        else:
            result += modality.process_format_directive(
                modality=modality, directive=chunk, index=index)

    return result