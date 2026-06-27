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
Module for testing the PATKIT saving operations and manifest generation.

This module validates that saving a session appends its metadata path
to the shared manifest file instead of overwriting existing scenarios.
"""

from pathlib import Path
from unittest.mock import MagicMock

from patkit.constants import PatkitConfigFile
from patkit.data_structures import Session
from patkit.save_and_load import save_manifest


def test_save_manifest_appends_scenarios(tmp_path: Path) -> None:
    """
    Verify that save_manifest appends unique session paths to the manifest.

    This test creates two distinct test scenarios with differing processing
    configurations in their respective 'patkit_data.yaml' files. Both
    scenarios target a common recorded data directory. The test ensures
    that calling save_manifest on both sessions results in a shared manifest
    file containing both path entries.

    Parameters
    ----------
    tmp_path : Path
        The pytest temporary directory fixture used to isolate file system
        side effects.

    Examples
    --------
    .. code-block:: python

        # Execute the test suite using pytest via uv or standard python
        pytest tests/test_save.py
    """
    # Define and create the shared recorded data directory structure
    recorded_data_dir = tmp_path / "recorded_data" / "minimal"
    recorded_data_dir.mkdir(parents=True, exist_ok=True)

    # Define the root directory for test scenarios
    test_scenarios_dir = tmp_path / "test_scenarios"
    test_scenarios_dir.mkdir(parents=True, exist_ok=True)

    # Setup scenario 1 directory for L1 norm processing
    scenario_1_dir = test_scenarios_dir / "scenario_l1"
    scenario_1_dir.mkdir(parents=True, exist_ok=True)

    # Setup scenario 2 directory for L2 and L3 norm processing
    scenario_2_dir = test_scenarios_dir / "scenario_l2_l3"
    scenario_2_dir.mkdir(parents=True, exist_ok=True)

    # Write the specific patkit_data.yaml for the first scenario.
    # This configuration contains all mandatory fields for DataConfig.
    yaml_path_1 = scenario_1_dir / "patkit_data.yaml"
    yaml_content_1 = (
        "epsilon: 0.00001\n"
        "mains_frequency: 50\n"
        "recorded_data_path: \"../../recorded_data/minimal\"\n"
        "flags:\n"
        "  detect_beep: True\n"
        "  test: False\n"
        "pd_arguments:\n"
        "  norms:\n"
        "    - 'l1'\n"
        "  timesteps:\n"
        "    - 1\n"
        "  mask_images: False\n"
        "  pd_on_interpolated_data: False\n"
        "  release_data_memory: True\n"
        "  preload: True\n"
    )
    with open(yaml_path_1, mode="w", encoding="UTF-8") as file:
        file.write(yaml_content_1)

    # Write the specific patkit_data.yaml for the second scenario.
    yaml_path_2 = scenario_2_dir / "patkit_data.yaml"
    yaml_content_2 = (
        "epsilon: 0.00001\n"
        "mains_frequency: 50\n"
        "recorded_data_path: \"../../recorded_data/minimal\"\n"
        "flags:\n"
        "  detect_beep: True\n"
        "  test: False\n"
        "pd_arguments:\n"
        "  norms:\n"
        "    - 'l2'\n"
        "    - 'l3'\n"
        "  timesteps:\n"
        "    - 1\n"
        "  mask_images: False\n"
        "  pd_on_interpolated_data: False\n"
        "  release_data_memory: True\n"
        "  preload: True\n"
    )
    with open(yaml_path_2, mode="w", encoding="UTF-8") as file:
        file.write(yaml_content_2)

    # Establish full paths to the expected session metadata files
    meta_path_1 = str((scenario_1_dir / "Session.meta").resolve())
    meta_path_2 = str((scenario_2_dir / "Session.meta").resolve())

    # Create a mock Session object for the first configuration
    session_l1 = MagicMock(spec=Session)
    session_l1.recorded_path = recorded_data_dir
    session_l1.patkit_meta_path = meta_path_1

    # Create a mock Session object for the second configuration
    session_l2_l3 = MagicMock(spec=Session)
    session_l2_l3.recorded_path = recorded_data_dir
    session_l2_l3.patkit_meta_path = meta_path_2

    # Invoke save_manifest for the first session to initialize the manifest
    save_manifest(session=session_l1)

    # Invoke save_manifest for the second session to append to the manifest
    save_manifest(session=session_l2_l3)

    # Construct the path to the resulting manifest file
    manifest_file = recorded_data_dir / PatkitConfigFile.MANIFEST

    # Confirm that the manifest file was successfully generated
    assert manifest_file.exists()

    # Read the manifest file contents to verify both entries are present
    with open(manifest_file, mode="r", encoding="UTF-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    # Verify that both scenario metadata file paths exist in the manifest
    assert meta_path_1 in lines
    assert meta_path_2 in lines
    assert len(lines) == 2
