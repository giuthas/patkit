from pathlib import Path

# Importing from save_and_load as requested
from patkit.save_and_load import (
    package_exercise_to_zip,
    unpackage_exercise_from_zip
)


def test_package_and_unpackage_exercise_filters_correctly(
    tmp_path: Path
) -> None:
    """
    Test that packaging an exercise correctly filters out root-level TextGrids
    and non-active answers, while renaming the active answer to 'answer'.
    """
    # 1. Setup a mock session directory structure
    session_path = tmp_path / "session"
    session_path.mkdir()

    # Normal file that should be included
    (session_path / "config.json").write_text('{"mock": "data"}')

    # Root-level TextGrid (should be filtered out by default)
    (session_path / "root_recording.TextGrid").write_text("root grid content")

    # Setup exercise answers directory
    answers_dir = session_path / "exercise" / "answers"
    answers_dir.mkdir(parents=True)

    # Active answer (should be included, but renamed to 'answer')
    active_ans_dir = answers_dir / "target_user"
    active_ans_dir.mkdir()
    (active_ans_dir / "annotation.TextGrid").write_text("active grid content")

    # Other answer (should be filtered out)
    other_ans_dir = answers_dir / "other_user"
    other_ans_dir.mkdir()
    (other_ans_dir / "annotation.TextGrid").write_text("other grid content")

    zip_path = tmp_path / "test_exercise.zip"

    # 2. Execute the packaging
    package_exercise_to_zip(
        session_path=session_path,
        zip_path=zip_path,
        active_answer_name="target_user",
        include_textgrids=False
    )

    assert zip_path.exists(), "The zip file was not created."

    # 3. Execute the unpackaging
    extract_path = tmp_path / "extracted"
    extract_path.mkdir()

    unpackage_exercise_from_zip(
        zip_filepath=zip_path,
        destination_directory=extract_path
    )

    # 4. Assertions on the unpacked directory structure
    assert (extract_path /
            "config.json").exists(), "Standard files should be retained."

    # Check that root-level TextGrids were ignored
    assert not (extract_path / "root_recording.TextGrid").exists(
    ), "Root TextGrids should be filtered out by default."

    # Check that the other user's answer was removed
    assert not (extract_path / "exercise" / "answers" /
                "other_user").exists(), "Inactive answers must be excluded."

    # Check that the original target user folder name no longer exists...
    assert not (
        extract_path / "exercise" / "answers" / "target_user"
    ).exists(), "The active answer should have been renamed."

    # ...and was properly renamed to 'answer'
    renamed_ans_dir = extract_path / "exercise" / "answers" / "answer"
    assert renamed_ans_dir.exists(
    ), "The target answer directory should be renamed to 'answer'."
    assert (renamed_ans_dir / "annotation.TextGrid").exists()
    assert (renamed_ans_dir /
            "annotation.TextGrid").read_text() == "active grid content"


def test_package_exercise_include_textgrids_flag(tmp_path: Path) -> None:
    """
    Test that setting include_textgrids=True bypasses the root-level
    TextGrid filtering logic.
    """
    session_path = tmp_path / "session"
    session_path.mkdir()

    # Root-level TextGrid
    (session_path / "root_recording.TextGrid").write_text("root grid content")

    # Minimal answers dir setup
    answers_dir = session_path / "exercise" / "answers" / "target_user"
    answers_dir.mkdir(parents=True)
    (answers_dir / "dummy.txt").write_text("data")

    zip_path = tmp_path / "test_with_grids.zip"

    # Package with the flag set to True
    package_exercise_to_zip(
        session_path=session_path,
        zip_path=zip_path,
        active_answer_name="target_user",
        include_textgrids=True
    )

    extract_path = tmp_path / "extracted"
    extract_path.mkdir()
    unpackage_exercise_from_zip(zip_path, extract_path)

    # The root TextGrid should now be present in the extracted archive
    assert (extract_path / "root_recording.TextGrid").exists(
    ), "Root TextGrid should be included when include_textgrids=True."
