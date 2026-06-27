#!/usr/bin/env python3
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
Simulate data and run metrics on it with plotting.

Original version was published for Ultrafest 2024.
"""

from functools import partial

import click
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from patkit.constants import ComparisonMember
from patkit.configuration import SimulationConfig
from patkit.utility_functions import product_dict
from patkit.metrics.calculate_spline_metric import (
    # spline_diff_metric,
    spline_nnd_metric, spline_shape_metric
)

from .contour_tools import generate_contour
from .metric_calculations import (
    calculate_metric_series_for_comparisons,
    calculate_metric_series_for_contours,
    get_distance_metric_baselines,
    get_shape_metric_baselines,
)
from .perturbation_series_plots import mci_perturbation_series_plot
from .rays_on_contours import (
    distance_metric_rays_on_contours,
    shape_metric_rays_on_contours,
)
from .simulation_datastructures import (
    Comparison,
    ComparisonSoundPair,
    DistanceMetricSimulationResult,
    ShapeMetricSimulationResult,
)
from .simulation_plots import make_demonstration_contour_plot


def _sort_comparisons(
        comparisons: list[Comparison],
        sort_by: ComparisonMember = ComparisonMember.FIRST,
) -> list[Comparison]:
    matching = [
        comparison for comparison in comparisons
        if comparison.first == comparison.second
    ]
    matching.sort(key=lambda comparison: comparison.first)

    non_matching = [
        comparison for comparison in comparisons
        if comparison.first != comparison.second
    ]
    if sort_by == ComparisonMember.FIRST:
        non_matching.sort(key=lambda comparison: comparison.first)
    else:
        non_matching.sort(key=lambda comparison: comparison.second)
    matching.extend(non_matching)
    return matching


def run_simulations(
        sim_configuration: SimulationConfig,
        contours: dict[str, np.ndarray],
        comparisons: list[Comparison],
        sound_pairs: list[ComparisonSoundPair],
) -> None:
    """
    Run simulations.

    Currently, runs only spline/contour simulations.

    Parameters
    ----------
    sim_configuration : SimulationConfig
        The configuration specifying the simulation to run.
    contours : dict[str, np.ndarray]
        Dict of ndarrays/tongue contours indexed by the IPA character of the
        corresponding sound.
    comparisons : list[Comparison]
        List of Comparisons to perform between the contours for distance metric
        simulation.
    sound_pairs : list[ComparisonSoundPair]
        List of sound pairs to be used in plotting.
    """
    distance_results = simulate_contour_distance_metrics(
        sim_configuration=sim_configuration,
        comparisons=comparisons,
        contours=contours,
    )
    shape_results = simulate_contour_shape_metrics(
        sim_configuration=sim_configuration,
        contours=contours,
    )

    save_result_figures(
        sim_configuration=sim_configuration,
        contours=contours,
        sound_pairs=sound_pairs,
        distance_metric_results=distance_results,
        shape_metric_results=shape_results,
    )


def simulate_contour_distance_metrics(
        sim_configuration: SimulationConfig,
        comparisons: list[Comparison],
        contours: dict[str, np.ndarray],
) -> list[DistanceMetricSimulationResult]:
    """
    Simulate contour shape metrics on splines.

    Parameters
    ----------
    sim_configuration : SimulationConfig
        Configuration variables for the simulation.
    comparisons : list[Comparison]
        List of Comparisons specifying which contour to compare to which and
        which of the two contours should be perturbed.
    contours : dict[str, np.ndarray]
        Dict of contours to run the simulation on: ndarrays indexed by the IPA
        character of the corresponding sound.

    Returns
    -------
    list[DistanceMetricSimulationResult]
        List of DistanceMetricSimulationResult containing the simulation
        results.
    """
    results = []
    for metric in sim_configuration.contour_distance.metrics:
        call = partial(
            spline_nnd_metric,
            metric=metric,
            timestep=sim_configuration.contour_distance.timestep,
            notice_base=sim_configuration.logging_notice_base,
        )
        result = calculate_metric_series_for_comparisons(
            metric=call,
            contours=contours,
            comparisons=comparisons,
            perturbations=sim_configuration.perturbations,
            interleave=True
        )
        baseline = get_distance_metric_baselines(
            metric=call, contours=contours)
        results.append(
            DistanceMetricSimulationResult(
                metric=metric, results=result, baselines=baseline
            )
        )
    return results


def simulate_contour_shape_metrics(
        sim_configuration: SimulationConfig,
        contours: dict[str, np.ndarray],
) -> list[ShapeMetricSimulationResult]:
    """
    Simulate contour shape metrics on splines.

    Parameters
    ----------
    sim_configuration : SimulationConfig
        Configuration variables for the simulation.
    contours : dict[str, np.ndarray]
        Dict of contours to run the simulation on: ndarrays indexed by the IPA
        character of the corresponding sound.

    Returns
    -------
    list[ShapeMetricSimulationResult]
        List of ShapeMetricSimulationResults containing the simulation results.
    """
    results = []
    for metric in sim_configuration.contour_shape.metrics:
        call = partial(
            spline_shape_metric,
            metric=metric,
            notice_base=sim_configuration.logging_notice_base,
        )
        result = calculate_metric_series_for_contours(
            metric=call,
            contours=contours,
            perturbations=sim_configuration.perturbations
        )
        baseline = get_shape_metric_baselines(
            metric=call,
            contours=contours,
        )
        results.append(
            ShapeMetricSimulationResult(
                metric=metric, baselines=baseline, results=result
            )
        )
    return results


def setup_contours_comparisons_soundpairs(
        sim_configuration: SimulationConfig
) -> tuple[dict[str, np.ndarray], list[Comparison], list[ComparisonSoundPair]]:
    """
    Set up the contours, Comparisons and ComparisonSoundPairs for a simulation.

    Parameters
    ----------
    sim_configuration : SimulationConfig
        The SimulationConfig

    Returns
    -------
    tuple[dict[str, np.ndarray], list[Comparison], list[ComparisonSoundPair]]
        First member is a dict of the contours indexed by sound, followed by
        lists of the Comparisons and ComparisonSoundPairs.
    """
    save_path = sim_configuration.output_directory
    if not save_path.exists():
        save_path.mkdir()
    sounds = sim_configuration.sounds
    contours = {
        sound: generate_contour(sound) for sound in sounds
    }

    comparison_generation = {
        "first": sounds,
        "second": sounds,
        "perturbed": ["first", "second"],
    }
    comparison_params = product_dict(**comparison_generation)
    comparisons = [
        Comparison(**params) for params in comparison_params
    ]

    sound_pair_generation = {
        "first": sounds,
        "second": sounds,
    }
    sound_pair_params = product_dict(**sound_pair_generation)
    sound_pairs = [
        ComparisonSoundPair(**params) for params in sound_pair_params
    ]
    return contours, comparisons, sound_pairs


def save_result_figures(
        sim_configuration: SimulationConfig,
        contours: dict[str, np.ndarray],
        sound_pairs: list[ComparisonSoundPair],
        distance_metric_results: list[DistanceMetricSimulationResult],
        shape_metric_results: list[ShapeMetricSimulationResult],
) -> None:
    """
    Plot and save result figures based on the directives in simulation config.

    Parameters
    ----------
    sim_configuration : SimulationConfig
        The configuration for the simulation including plotting directives.
    contours : dict[str, np.ndarray]
        The contours the simulation was run on. Dict of ndarrays indexed by the
        IPA characters of the corresponding sound.
    sound_pairs : list[ComparisonSoundPair]
        The sound pairs th simulation was run on.
    distance_metric_results : list[DistanceMetricSimulationResult]
        Results from distance metric simulations.
    shape_metric_results : list[ShapeMetricSimulationResult]
        Results from shape metric simulations.
    """
    save_dir = sim_configuration.output_directory
    perturbations = sim_configuration.perturbations

    saved_figures = False

    if sim_configuration.distance_metric_ray_plot is not None:
        ray_plot_params = sim_configuration.distance_metric_ray_plot
        for distance_metric_result in distance_metric_results:
            save_path = (
                save_dir / f"{distance_metric_result.metric}_contours.pdf")
            write_plot = _determine_plot_writing(save_path, sim_configuration)
            if write_plot:
                with PdfPages(save_path) as pdf:
                    distance_metric_rays_on_contours(
                        contours=contours,
                        distance_metric_result=distance_metric_result,
                        number_of_perturbations=len(perturbations),
                        columns=sound_pairs,
                        ray_plot_params=ray_plot_params,
                    )
                    plt.tight_layout()
                    pdf.savefig(plt.gcf())
                    saved_figures = True

    if sim_configuration.shape_metric_ray_plot is not None:
        ray_plot_params = sim_configuration.shape_metric_ray_plot
        for shape_metric_result in shape_metric_results:
            save_path = (
                save_dir / f"{shape_metric_result.metric}_contours.pdf")
            write_plot = _determine_plot_writing(save_path, sim_configuration)
            if write_plot:
                with PdfPages(save_path) as pdf:
                    shape_metric_rays_on_contours(
                        contours=contours,
                        shape_metric_result=shape_metric_result,
                        ray_plot_params=ray_plot_params,
                        number_of_perturbations=len(perturbations),
                    )
                    plt.tight_layout()
                    pdf.savefig(plt.gcf())
                    saved_figures = True

    if sim_configuration.mci_perturbation_series_plot:
        mci_config = sim_configuration.mci_perturbation_series_plot
        save_path = save_dir / mci_config.filename

        write_plot = _determine_plot_writing(save_path, sim_configuration)
        if write_plot:
            with PdfPages(save_path) as pdf:
                mci_perturbation_series_plot(
                    contours=contours,
                    perturbations=perturbations,
                    figure_size=mci_config.figure_size,
                )
                pdf.savefig(plt.gcf())
                saved_figures = True

    if sim_configuration.demonstration_contour_plot is not None:
        plot_params = sim_configuration.demonstration_contour_plot
        save_path = save_dir / plot_params.filename

        write_plot = _determine_plot_writing(save_path, sim_configuration)
        if write_plot:
            with PdfPages(save_path) as pdf:
                make_demonstration_contour_plot(
                    contour_1=contours[plot_params.sounds[0]],
                    contour_2=contours[plot_params.sounds[1]],
                    figure_size=plot_params.figure_size,
                )
                pdf.savefig(plt.gcf())
                saved_figures = True

    if saved_figures:
        print(f"Saved simulation figures in {save_dir}.")


def _determine_plot_writing(save_path, sim_configuration):
    if save_path.exists():
        write_plot = False
        if sim_configuration.overwrite_plots is None:
            write_plot = click.confirm(
                f"{save_path} exists.\n"
                f"Do you want to overwrite the file?"
            )
        elif sim_configuration.overwrite_plots is True:
            write_plot = True
    else:
        write_plot = True
    return write_plot
