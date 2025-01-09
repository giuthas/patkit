#
# Copyright (c) 2019-2025
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
SATKIT Commandline.
"""

import click

from . import satkit_click


@click.group()
@click.version_option()
@click.pass_context
@click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=True, file_okay=True), )
@click.argument("config_file")
def run_cli(context: click.Context, path, config_file) -> None:
    """
    SATKIT - Speech Analysis ToolKIT

    Satkit collects tools for phonetic analysis of speech data. It includes
    tools for analysing audio and articulatory data, a commandline interface, an
    annotator GUI, and a Python programming API. See documentation for more
    details.

    By default, Satkit will open the given path in the annotator GUI.
    """
    print("in run_cli")
    satkit_click.open_in_annotator(path, config_file)


# noinspection PyTypeChecker
run_cli.add_command(satkit_click.open_in_annotator)
# noinspection PyTypeChecker
run_cli.add_command(satkit_click.interact)
