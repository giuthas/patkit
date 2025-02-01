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
patkit interactive interpreter.
"""
import atexit
import code
import os
import readline
import rlcompleter

from patkit.configuration import Configuration
from patkit.constants import PATKIT_CONFIG_DIR, PATKIT_HISTORY_FILE
from patkit.data_structures import Session


def run_interpreter(session: Session, configuration: Configuration):
    """
    Run the patkit interactive interpreter on the command line.

    Parameters
    ----------
    session : Session
        The loaded Session.
    configuration : Configuration
        The Configuration for this run.
    """
    # TODO 1.0: Might be better doing this with IPython than the history-less
    # standard library version
    # import IPython
    # IPython.embed()

    variables = locals()
    readline.set_completer(rlcompleter.Completer(variables).complete)
    # readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("bind ^I rl_complete")

    python_history_file = os.path.expanduser(PATKIT_HISTORY_FILE)
    config_dir = os.path.expanduser(PATKIT_CONFIG_DIR)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if os.path.exists(python_history_file):
        readline.read_history_file(python_history_file)
    atexit.register(readline.write_history_file, python_history_file)

    code.InteractiveConsole(variables).interact(
        banner="patkit Interactive Console",
        exitmsg="Exiting patkit Interactive Console",
    )
