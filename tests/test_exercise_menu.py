"""Tests for the Exercise menu functionality in PdQtAnnotator."""

from unittest.mock import MagicMock

from patkit.constants import AnnotatorMode, ExerciseMode, ExerciseScrambler
from patkit.gui import NewExerciseDialog, NewAnswerDialog
from patkit.qt_annotator import PdQtAnnotator


def test_new_exercise_success(
    annotator: PdQtAnnotator,
    mocker: MagicMock,
) -> None:
    """Test successful creation of a new exercise."""
    # mock_path = Path("/dummy/path/exercise_1")
    mock_scrambler = ExerciseScrambler.EQUIDISTANT

    # 1. Intercept the static method directly on the class
    mocker.patch.object(
        NewExerciseDialog, "get_exercise_params",
        return_value=mock_scrambler
    )

    # 2. Intercept the mandatory answer dialog directly on the class
    mocker.patch.object(
        NewAnswerDialog, "get_answer_params",
        return_value=("Test_Answer", "Test_Author")
    )

    # 3. Prevent Matplotlib from crashing on the fake test data
    mocker.patch.object(annotator.plot_controller, "draw_plots")
    mocker.patch("patkit.qt_annotator.save_exercise")

    # Execute the real logic
    result = annotator.new_exercise()

    # Verify everything actually worked!
    assert result is True
    assert annotator.session.exercise is not None
    assert annotator.session.exercise.name == "exercise"
    assert (
        annotator.session.exercise.metadata.scrambling_method == mock_scrambler
    )
    assert annotator.session.exercise.current_answer is not None
    assert (
        annotator.mode_drop_down.currentText() == AnnotatorMode.EXERCISE.value
    )


def test_new_exercise_cancelled(annotator, mocker):
    """Test new_exercise aborts gracefully when the dialog is cancelled."""
    mocker.patch(
        "patkit.qt_annotator.NewExerciseDialog.get_exercise_params",
        return_value=None
    )

    result = annotator.new_exercise()

    assert result is False


def test_save_exercise(annotator, mocker):
    """Test that save_exercise delegates to the native save function."""
    mock_save = mocker.patch("patkit.qt_annotator.save_exercise")
    dummy_exercise = MagicMock()
    annotator.session.exercise = dummy_exercise

    annotator.save_exercise()

    mock_save.assert_called_once_with(exercise=dummy_exercise)


def test_new_answer_success(annotator, mocker):
    """Test new answer creation generates an answer and updates the cursor."""
    mocker.patch(
        "patkit.qt_annotator.NewAnswerDialog.get_answer_params",
        return_value=("Answer_1", "AuthorName")
    )

    annotator.session.exercise = MagicMock()
    annotator.session.exercise.__len__.return_value = 5
    mocker.patch.object(annotator, "update")

    result = annotator.new_answer()

    assert result is True
    annotator.session.exercise.new_blank_answer.assert_called_once_with(
        name="Answer_1", author="AuthorName"
    )
    assert annotator.session.exercise.cursor == 4
    assert annotator.update.called


def test_new_answer_cancelled(annotator, mocker):
    """Test new answer halts if dialog is cancelled."""
    mocker.patch(
        "patkit.qt_annotator.NewAnswerDialog.get_answer_params",
        return_value=(None, None)
    )

    result = annotator.new_answer()

    assert result is False


def test_save_answer(annotator, mocker):
    """Test that save_answer delegates correctly for the current answer."""
    mock_save = mocker.patch("patkit.qt_annotator.save_answer")
    annotator.session.exercise = MagicMock()
    mock_current_answer = MagicMock()
    annotator.session.exercise.current_answer = mock_current_answer

    annotator.save_answer()

    mock_save.assert_called_once_with(answer=mock_current_answer)


def test_load_answer_success(annotator, mocker, tmp_path):
    """Test loading an answer from disk correctly maps it into the exercise."""
    # Setup dummy answer directories
    answers_dir = tmp_path / "answers"
    answers_dir.mkdir()
    (answers_dir / "Answer_1").mkdir()

    annotator.session.exercise = MagicMock()
    annotator.session.exercise.patkit_path = tmp_path

    mocker.patch(
        "patkit.qt_annotator.QInputDialog.getItem",
        return_value=("Answer_1", True)
    )

    mock_answer = MagicMock()
    mock_answer.name = "Answer_1"
    mocker.patch("patkit.qt_annotator.load_answer", return_value=mock_answer)

    annotator.session.exercise.keys.return_value = [
        "Existing_Answer", "Answer_1"]
    mocker.patch.object(annotator, "go_to_recording")
    mocker.patch.object(annotator, "update")
    mocker.patch.object(annotator, "update_ui")

    annotator.open_answer()

    # Verify the answer was loaded and dictionary set
    annotator.session.exercise.__setitem__.assert_called_once_with(
        "Answer_1", mock_answer)
    assert annotator.session.exercise.cursor == 1
    annotator.update.assert_called_once()
    annotator.update_ui.assert_called_once()
    annotator.go_to_recording.assert_called_once()


def test_show_example_toggles_mode(annotator):
    """Test the example toggle switches the drop-down mode properly."""
    # Test True
    annotator.action_show_example.setChecked(True)
    annotator.show_example()
    assert (
        annotator.exercise_drop_down.currentText() ==
        ExerciseMode.EXAMPLE.value
    )

    # Test False
    annotator.action_show_example.setChecked(False)
    annotator.show_example()
    assert (
        annotator.exercise_drop_down.currentText() ==
        ExerciseMode.ANSWER.value
    )


def test_to_annotator_mode(annotator, mocker):
    """
    Test the GUI locks exercise features when switching to annotator mode.
    """
    mocker.patch.object(annotator, "update")
    mocker.patch.object(annotator, "update_ui")
    annotator.plot_controller = MagicMock()

    annotator.to_annotator_mode()

    assert annotator.action_save_exercise.isEnabled() is False
    assert annotator.action_save_answer.isEnabled() is False
    assert annotator.exercise_drop_down.isEnabled() is False
    assert annotator.action_save_all_textgrids.isEnabled() is True
    assert annotator.action_save_current_textgrid.isEnabled() is True

    annotator.plot_controller.to_annotator_mode.assert_called_once_with(
        annotator.gui_color_mode
    )


def test_to_exercise_mode_with_existing_exercise(annotator, mocker):
    """Test the GUI unlocks exercise features when an exercise exists."""
    annotator.session.exercise = MagicMock()
    mocker.patch.object(annotator, "update")
    mocker.patch.object(annotator, "update_ui")
    annotator.plot_controller = MagicMock()

    annotator.to_exercise_mode()

    assert annotator.action_save_exercise.isEnabled() is True
    assert annotator.action_save_answer.isEnabled() is True
    assert annotator.exercise_drop_down.isEnabled() is True
    assert annotator.action_save_all_textgrids.isEnabled() is False
    assert annotator.action_save_current_textgrid.isEnabled() is False

    annotator.plot_controller.to_exercise_mode.assert_called_once_with(
        annotator.gui_color_mode
    )
