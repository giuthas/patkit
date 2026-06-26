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
from pathlib import Path


from patkit.constants import OpenPathType, PatkitConfigFile, SourceSuffix
from patkit.data_structures import Manifest


def resolve_open_path(path: Path) -> tuple[OpenPathType, Path]:
    """
    Resolve a given path into its logical type and canonical target path.

    This function classifies the input path for the 'patkit open' command
    into one of four categories: a manifest file, a scenario directory,
    a single data file, or a plain directory. It also returns the canonical
    path to be used (e.g., returning the parent directory if a scenario
    config file was directly provided).

    Parameters
    ----------
    path : Path
        The original path provided by the user.

    Returns
    -------
    tuple[OpenPathType, Path]
        A tuple containing the resolved path type enumeration and the
        canonical path to open.

    Raises
    ------
    FileNotFoundError
        If the provided path does not exist.
    ValueError
        If a provided file path does not match any recognized PATKIT file
        types or suffixes.
    """
    # Resolve to an absolute path for consistent processing
    path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(f"The path '{path}' does not exist.")

    # Dynamically build the set of scenario configurations from the Enum,
    # excluding the MANIFEST file which is handled as a distinct case.
    scenario_configs = {
        config for config in PatkitConfigFile
        if config != PatkitConfigFile.MANIFEST
    }

    if path.is_file():
        # Case 1: Direct path to a manifest file
        if path.name == PatkitConfigFile.MANIFEST:
            return OpenPathType.MANIFEST, path

        # Case 2: Direct path to a scenario configuration file
        if path.name in scenario_configs:
            return OpenPathType.SCENARIO, path.parent

        # Case 3: Direct path to a single recognized data file.
        # Because SourceSuffix inherits from str, .endswith() natively
        # accepts the Enum members as valid string arguments.
        for suffix in SourceSuffix:
            if path.name.endswith(suffix):
                return OpenPathType.SINGLE_DATA, path

        # Fail early and clearly if the file is completely unrecognized
        raise ValueError(
            f"The file '{path}' is not a recognized PATKIT configuration "
            f"or data file."
        )

    if path.is_dir():
        # Case 1: Directory containing a manifest file
        manifest_path = path / PatkitConfigFile.MANIFEST
        if manifest_path.is_file():
            return OpenPathType.MANIFEST, manifest_path

        # Case 2: Scenario directory containing patkit-data.yaml or others
        for config_name in scenario_configs:
            if (path / config_name).is_file():
                return OpenPathType.SCENARIO, path

        # Case 4: Directory without a manifest or patkit configuration
        return OpenPathType.DIRECTORY, path

    # Fallback for broken symlinks or unsupported file types (like sockets)
    raise ValueError(f"The path '{path}' is neither a file nor a directory.")


def get_manifest_scenarios(path: Path) -> list[Path] | None:
    """
    Read all scenario paths from a manifest.

    The paths will be resolved i.e. they will be absolute paths.

    Parameters
    ----------
    path : Path
        The original target path provided by the user.

    Returns
    -------
    list[Path] | None
        A list of resolved, absolute paths found in the manifest if a non-empty
        manifest was found. Returns None if no manifest was found or an empty
        list if it is empty.
    """
    if path.is_file():
        manifest_path = path
    elif path.is_dir():
        manifest_path = path / PatkitConfigFile.MANIFEST
        if not manifest_path.is_file():
            raise FileNotFoundError(
                f"Patkit manifest file not found in {path}.\n"
                f"Expected to find {PatkitConfigFile.MANIFEST}."
            )
    else:
        return None

    manifest = Manifest(path=manifest_path)

    resolved_paths = []
    for scenario in manifest:
        scenario_path = Path(scenario)
        if not scenario_path.is_absolute():
            scenario_path = (manifest_path.parent / scenario_path).resolve()

        resolved_paths.append(scenario_path)

    return resolved_paths
