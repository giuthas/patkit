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
"""Main configuration for patkit."""

import logging
from pathlib import Path

from patkit.constants import PatkitConfigFile
from .configuration_parsers import (
    load_gui_params, load_publish_params,
    load_data_params, load_simulation_params
)
from .configuration_models import (
    GuiConfig, DataConfig, PublishConfig, SimulationConfig
)

_logger = logging.getLogger('patkit.configuration')


class ConfigPaths:
    """
    Configuration paths of patkit.
    """

    def __init__(self, path: Path):
        self.path = path

    @property
    def data_config(self) -> Path | None:
        config_path = self.path/PatkitConfigFile.DATA
        if config_path.exists():
            return config_path
        return None

    @property
    def gui_config(self) -> Path | None:
        config_path = self.path/PatkitConfigFile.GUI
        if config_path.exists():
            return config_path
        return None

    @property
    def publish_config(self) -> Path | None:
        config_path = self.path/PatkitConfigFile.PUBLISH
        if config_path.exists():
            return config_path
        return None

    @property
    def simulation_config(self) -> Path | None:
        config_path = self.path/PatkitConfigFile.SIMULATION
        if config_path.exists():
            return config_path
        return None


class Configuration:
    """
    Main configuration class of patkit.
    """

    # TODO: implement save functionality.

    def __init__(
            self,
            configuration_paths: ConfigPaths
    ) -> None:
        """
        Init the main configuration object.

        Run only once. Updates should be done with methods of the class.

        Parameters
        -------
        configuration_paths : ConfigPaths
            Paths to load the configuration from.
        """
        # TODO 0.24 do reporting and logging on what gets loaded and where
        # from. this or similar for reporting
        # https://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
        self._config_paths = configuration_paths

        if self._config_paths.data_config is not None:
            self._data_yaml = load_data_params(
                self._config_paths.data_config)
            self._data_config = DataConfig(**self._data_yaml.data)
            recorded = \
                self._config_paths.path/self._data_config.recorded_data_path
            self._data_config.recorded_data_path = recorded.resolve()
        else:
            self._data_config = None

        if self._config_paths.gui_config is not None:
            self._gui_yaml = load_gui_params(self._config_paths.gui_config)
            self._gui_config = GuiConfig(**self._gui_yaml.data)
        else:
            self._gui_config = None

        if self._config_paths.publish_config is not None:
            self._publish_yaml = load_publish_params(
                self._config_paths.publish_config)
            self._publish_config = PublishConfig(**self._publish_yaml.data)
        else:
            self._publish_config = None

        if self._config_paths.simulation_config is not None:
            self._simulation_yaml = load_simulation_params(
                self._config_paths.simulation_config)
            self._simulation_config = SimulationConfig(
                **self._simulation_yaml.data)
        else:
            self._simulation_config = None

        # self._plot_yaml = load_plot_params(config['plotting_parameter_file'])
        # self._plot_config = PlotConfig(**self._plot_yaml.data)

    # TODO 0.28: Implement this for better tracing and/or ease of saving.
    # def __repr__(self) -> str:
    #     return (
    #         f"Configuration("
    #         f"\nmain config file={self._config_paths.path})"
    #         f"\ndata_run={self._data_config.model_dump()}"
    #         f"\ngui={self._gui_config.model_dump()}"
    #         f"\npublish={self._publish_config.model_dump()})"
    #         f"\nsimulate={self._simulation_config.model_dump()})"
    #     )

    @property
    def config_paths(self) -> ConfigPaths:
        """Main config Paths."""
        return self._config_paths

    @property
    def data_config(self) -> DataConfig | None:
        """Config options for a data run."""
        return self._data_config

    @data_config.setter
    def data_config(self, new_config: DataConfig) -> None:
        if isinstance(new_config, DataConfig):
            self._data_config = new_config
        else:
            raise ValueError(f"Expected a DataRunConfig instance. "
                             f"Found {new_config.__class__} instead.")

    @property
    def gui_config(self) -> GuiConfig:
        """Gui config options."""
        return self._gui_config

    @property
    def publish_config(self) -> PublishConfig | None:
        """Result publishing configuration options."""
        return self._publish_config

    @publish_config.setter
    def publish_config(self, new_config: PublishConfig) -> None:
        if isinstance(new_config, PublishConfig):
            self._data_config = new_config
        else:
            raise ValueError(f"Expected a PublishConfig instance. "
                             f"Found {new_config.__class__} instead.")

    @property
    def simulation_config(self) -> SimulationConfig:
        """Simulation configuration options."""
        return self._simulation_config

    def save_to_file(
            self, filename: Path | str
    ) -> None:
        """
        Save configuration to a file.

        Parameters
        ----------
        filename : Path | str
            File to save to.

        Raises
        ------
        NotImplementedError
            This hasn't been implemented yet.
        """
        # filename = path_from_name(filename)
        # with open(filename, 'w') as file:
        # TODO: the problem here is that we can't write Configuration to a
        #   single file.
        #     file.write(self)

        raise NotImplementedError(
            "Saving configuration to a file has not yet been implemented.")

    def update_data_config_from_file(
            self, configuration_file: Path | str
    ) -> None:
        """
        Update the data run configuration from a file.

        Parameters
        ----------
        configuration_file : Path | str
            File to read the new options from.
        """
        self._data_yaml = load_data_params(filepath=configuration_file)
        if self._data_config is None:
            self._data_config = DataConfig(**self._data_yaml.data)
        else:
            self._data_config.update(self._data_yaml.data)

    def update_publish_from_file(self, configuration_file: Path | str) -> None:
        """
        Update the publishing configuration from a file.

        Parameters
        ----------
        configuration_file : Path | str
            File to read the new options from.
        """
        self._publish_yaml = load_publish_params(filepath=configuration_file)
        if self._publish_config is None:
            self._publish_config = DataConfig(**self._publish_yaml.data)
        else:
            self._publish_config.update(self._publish_yaml.data)

    def update_gui_from_file(self, configuration_file: Path | str) -> None:
        """
        Update the GUI configuration from a file.

        Parameters
        ----------
        configuration_file : Path | str
            File to read the new options from.
        """
        self._gui_yaml = load_publish_params(filepath=configuration_file)
        if self._gui_config is None:
            self._gui_config = DataConfig(**self._gui_yaml.data)
        else:
            self._gui_config.update(self._gui_yaml.data)

    # TODO 0.25 updating needs some attention or disabling. simulation missing
    # at least
    def update_all_from_files(
            self, configuration_paths: ConfigPaths
    ) -> None:
        """
        Update the configuration from a file.

        This first updates the main configuration and then recursively updates
        the other configuration members.

        NOTE: comment round tripping may/will be broken by running any of the
        update methods.

        Parameters
        ----------
        configuration_paths : ConfigPaths
            Paths to load the configuration from.
        """
        self._config_paths = configuration_paths
        if self.config_paths.data_config is not None:
            self.update_data_config_from_file(
                self.config_paths.data_config
            )
        if self.config_paths.gui_config is not None:
            self.update_gui_from_file(self._config_paths.gui_config)
        if self.config_paths.publish_config is not None:
            self.update_publish_from_file(
                self._config_paths.publish_config
            )
