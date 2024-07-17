import pytest
from PySide2.QtWidgets import QPushButton, QMessageBox, QDialog, QApplication
from PySide2.QtCore import Qt, QTimer
from function_plotter import FunctionPlotter
import time
from typing import Callable, Optional

# thanks to https://github.com/pytest-dev/pytest-qt/issues/256
def get_dialog(dialog_trigger: Callable, time_out: int = 5) -> QDialog:
    """
    Returns the current dialog (active modal widget). If there is no
    dialog, it waits until one is created for a maximum of 5 seconds (by
    default).

    :param dialog_trigger: Callable that triggers the dialog creation.
    :param time_out: Maximum time (seconds) to wait for the dialog creation.
    """
    dialog: Optional[QDialog] = None
    start_time = time.time()

    # Helper function to catch the dialog instance and hide it
    def dialog_creation():
        # Wait for the dialog to be created or timeout
        nonlocal dialog
        while dialog is None and time.time() - start_time < time_out:
            dialog = QApplication.activeModalWidget()

        # Avoid errors when dialog is not created
        if dialog is not None:
            # Hide dialog to avoid interrupting the tests execution
            # It has the same effect as close()
            dialog.hide()

    # Create a thread to get the dialog instance and call dialog_creation trigger
    QTimer.singleShot(1, dialog_creation)  
    dialog_trigger()

    # Wait for the dialog to be created or timeout
    while dialog is None and time.time() - start_time < time_out:
        continue

    assert isinstance(
        dialog, QDialog
    ), f"No dialog was created after {time_out} seconds. Dialog type: {type(dialog)}"

    return dialog

# fixture to initialize the application with qtbot for testing
@pytest.fixture
def app(qtbot):
    test_app = FunctionPlotter()
    qtbot.addWidget(test_app)
    return test_app

# helper function to test invalid inputs
# if you want change the fn name to test_.. uncomment the next line
# @pytest.mark.skip(reason="This is a helper function and should not be run as a test.")
def helper_invalid_input(app, qtbot, function_input, x_min_input, x_max_input, expected_error_message):
    app.function_input.setText(function_input)
    app.x_min_input.setText(x_min_input)
    app.x_max_input.setText(x_max_input)
    plot_button = app.findChild(QPushButton, text="Plot")
    assert plot_button is not None

    def trigger_dialog():
        qtbot.mouseClick(plot_button, Qt.LeftButton)

    error_msg_box = get_dialog(trigger_dialog)

    assert error_msg_box.windowTitle() == "Error"
    assert error_msg_box.text() == expected_error_message
    assert error_msg_box.icon() == QMessageBox.Critical

    ok_button = error_msg_box.button(QMessageBox.Ok)
    qtbot.mouseClick(ok_button, Qt.LeftButton)

    assert app.findChild(QMessageBox) is None

def test_empty_function_input(app, qtbot):
    helper_invalid_input(app, qtbot, "", "-5", "5", "Please enter a function.")

def test_invalid_function_input(app, qtbot):
    helper_invalid_input(app, qtbot, "5*x**", "-5", "5", "Invalid function input. Please check your syntax.")

def test_invalid_min_x(app, qtbot):
    helper_invalid_input(app, qtbot, "5*x", "invalid", "5", "Invalid minimum value for x.")

def test_invalid_max_x(app, qtbot):
    helper_invalid_input(app, qtbot, "5*x", "-5", "invalid", "Invalid maximum value for x.")

def test_min_x_greater_than_max_x(app, qtbot):
    helper_invalid_input(app, qtbot, "5*x", "5", "-5", "Minimum x must be less than maximum x.")

def test_basic(app, qtbot):
    app.function_input.setText("5*x")
    app.x_min_input.setText("-5")
    app.x_max_input.setText("5")

    plot_button = app.findChild(QPushButton, text="Plot")
    assert plot_button is not None
    
    qtbot.mouseClick(plot_button, Qt.LeftButton)

    assert app.ax.has_data()

    # check if the plotted data is correct
    lines = app.ax.get_lines()
    assert len(lines) == 1  # there should be one line plotted

    # get the line data
    line = lines[0]
    x_data, y_data = line.get_data()

    assert len(x_data) > 0
    assert len(y_data) > 0

    assert app.ax.get_xlabel() == 'x'
    assert app.ax.get_ylabel() == 'f(x)'
    assert app.ax.get_title() == 'Plot of the function'

    legend_texts = [text.get_text() for text in app.ax.get_legend().get_texts()]
    print(legend_texts)
    assert legend_texts == ['$5 x$']