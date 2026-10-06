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

from patkit.configuration import PathStructure, SessionConfig
from patkit.constants import DatasourceNames
from patkit.data_structures import (
    Exercise, Session,
    ExerciseMetadata, FileInformation
)
from patkit.save_and_load import load_exercise, save_exercise


def test_answer_cursor_save_and_load(tmp_path: Path) -> None:
    """
    Verify that an Answer's cursor position is accurately preserved
    when an Exercise is saved to disk and subsequently loaded.
    """
    # Setup minimal dependencies for the Exercise
    file_info = FileInformation(patkit_path=tmp_path)
    path_structure = PathStructure(root=tmp_path)
    session = Session(
        name="test_session",
        config=SessionConfig(
            data_source_name=DatasourceNames.WAV,
            path_structure=path_structure),
        file_info=file_info
    )

    ex_metadata = ExerciseMetadata()
    exercise = Exercise(
        scenario=session,
        name="TestExercise",
        metadata=ex_metadata,
        file_info=file_info
    )

    # Create a new answer and artificially advance the cursor
    exercise.new_blank_answer(cursor=0, name="TestAnswer")
    answer = exercise["TestAnswer"]

    # Move the cursor to simulate user interaction
    expected_cursor_position = 2
    answer.cursor = expected_cursor_position

    # Save the exercise to the temporary path
    save_exercise(exercise=exercise)

    # Load the exercise from the temporary path
    loaded_exercise = load_exercise(directory=tmp_path, scenario=session)
    loaded_answer = loaded_exercise["TestAnswer"]

    # Assert the cursor state natively crashes if invalid
    assert loaded_answer.cursor == expected_cursor_position
