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
SATKIT command line commands.
"""

import code
from pathlib import Path

import click

from .initialise import (
    add_derived_data, initialise_satkit, run_annotator
)
from .utility_functions import log_elapsed_time


@click.command(name="open")
@click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=True, file_okay=True), )
@click.argument(
    "config_file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=False,
)
def open_in_annotator(path: Path, config_file: Path | None):
    """
    Open the PATH in the annotator GUI.

    \b
    PATH to the data - maybe be a file or a directory.
    CONFIG_FILE configuration .yaml file.

    NOT IMPLEMENTED YET.
    """
    # TODO 0.14: remove the dependency on argparse
    # TODO 0.14: move add_derived_data into initialise_satkit
    # TODO 0.14: update the other commands too

    if config_file is None:
        config_file = Path("configuration/configuration.yaml")
    configuration, logger, session = initialise_satkit(
        path=path, config_file=config_file)
    log_elapsed_time(logger)

    add_derived_data(session=session, config=configuration)
    log_elapsed_time(logger)

    run_annotator(session, configuration)


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=True, file_okay=True), )
@click.argument("config_file")
def interact():
    """
    Open the PATH in interactive commandline mode.

    \b
    PATH to the data - maybe be a file or a directory.
    CONFIG_FILE configuration .yaml file.

    NOT IMPLEMENTED YET.
    """
    configuration, logger, session = initialise_satkit()
    log_elapsed_time(logger)

    add_derived_data(session=session, config=configuration)
    log_elapsed_time(logger)

    # TODO 1.0: Probably better doing this with IPython than the history-less
    # standard library version
    # import IPython
    # IPython.embed()
    code.interact(
        banner="SATKIT Interactive Console",
        local=locals(),
        exitmsg="Exiting SATKIT Interactive Console",
    )

