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
SATKIT -- The Speech Articulation ToolKIT

SATKIT consists of several interdependent modules.

![SATKIT Module hierarchy](packages_satkit.png "SATKIT Module hierarchy")

SATKIT's data structures are built around two class hierarchies: 
The Recording and the Modality. Similarly the commandline interface -- and 
the batch processing of data -- is handled by classes that extend CLI and 
graphical annotation tools derive from Annotator.

![SATKIT Class hierarchies](classes_satkit.png "SATKIT Class hierarchies")
"""

import json
import logging
import logging.config

# import satkit.configuration.configuration as configuration
from satkit.helpers.logging_helpers import log_elapsed_time, set_logging_level

# Load logging config from json file.
LOG_CONFIG = "configuration/satkit_logging_configuration.json"
with open(LOG_CONFIG, 'r', encoding='utf-8') as configuration_file:
    config_dict = json.load(configuration_file)
    logging.config.dictConfig(config_dict)

# Create the module logger.
_satkit_logger = logging.getLogger('satkit')

# Log that the logger was configured.
_satkit_logger.info('Completed configuring logger.')

# Config should be loaded before parsing arguments, because it may affect
# how arguments are parsed, and parsed arguments may change config variables.

# TODO: later on make this more complex: parts of config that could be changed by
# args first, args second, rest of config last. should probably be close to
# where different commands will eventually be dealt with

# configuration.load_config()
