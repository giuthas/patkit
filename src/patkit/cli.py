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
PATKIT Commandline main command.
"""

import click
from click_default_group import DefaultGroup

from patkit import cli_commands


@click.group(
    cls=DefaultGroup, default='open', default_if_no_args=False)
@click.pass_context
@click.option('--verbosity', '-v', default=1, show_default=True)
@click.version_option()
def run_cli(
        context: click.Context,
        verbosity: int
) -> None:
    """
    patkit - Phonetic Analysis ToolKIT

    Patkit collects tools for phonetic analysis of speech data. It includes
    tools for analysing audio and articulatory data, a commandline interface, an
    annotator GUI, and a Python programming API. See documentation for more
    details.

    By default, patkit will open the given path in the annotator GUI.
    """


# noinspection PyTypeChecker
run_cli.add_command(cli_commands.open_in_annotator)
# noinspection PyTypeChecker
run_cli.add_command(cli_commands.interact)
# noinspection PyTypeChecker
run_cli.add_command(cli_commands.simulate)
