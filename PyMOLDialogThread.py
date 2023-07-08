# Serena Rosignoli, 2023

################################################################
#### How to run a Thread process from a Dialog in a PyMOL plugin.
################################################################

# !! THIS CODE:
# !! - is not intended for standalone running.
# !! - must be adapted to an existing PyMOL plugin
# !! - must be read as a tutorial

#### -  Import PyMOL and PyQt5 libraries.
import pymol
from pymol import cmd
from pymol.Qt import QtWidgets, QtCore, QtGui

from pymol import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QProcess

#### 1. Insert BLOCK 1 in a Class Instance of your PyMOL plugin
#### 2. The function to be called for visualizing the Dialog is 'initDialog()'

################################## CODE-BLOCK 1 ###############################################################

def initDialog(self): #### 2.

    ### 2a. Initialize DialogThread object
    self.DIALOG = DialogThread(self)

    ### 2b. Setup the DialogThread
    ###   - The function to run the desired process (i.e. self.run_job) is passed as input
    ###   - See DialogThread Class for further details about 'setup_thread'
    self.DIALOG.setup_thread(self.run_job)

    ### 2c. Setup signal-event connection
    ###   - See (DialogThread)-JobThread Class for further details about the 'connect' function
    self.DIALOG.jobthread.emit_exception.connect(self.on_emit_exception)
    self.DIALOG.jobthread.update_progress_text.connect(self.on_update_progress_text)
    self.DIALOG.jobthread.process_completed.connect(self.on_process_completed)
    self.DIALOG.jobthread.update_progressbar.connect(self.on_update_progressbar)

    ### 2d. Setup the layout
    ###   - The DialogThread object is passed as input
    ###   - setup the Dialog UI in 'initThreadDialogUI' function
    self.initThreadDialogUI(self.DIALOG)

    ### 2e. Execute
    self.DIALOG.setModal(True)
    self.DIALOG.exec_()


def initThreadDialogUI(self, dialog):

    '''
    Setup layout of the DialogThread.
    The 'dialog' in input is a DialogThread Object
    '''

    ## set the dialog as self
    parent_class = self
    self = dialog

    ## Window setup
    self.setWindowTitle('Title')
    self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
    self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
    self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)

    ## Layouts
    vertical_layout = QtWidgets.QVBoxLayout()
    horizontal_layout = QtWidgets.QHBoxLayout()

    ## Insert widgets for the Main Dialog Box ('vertical_layout')
    self.progress_bar = QtWidgets.QProgressBar(self)
    vertical_layout.addWidget(self.progress_bar)
    # ...
    # ... other widgets ...
    # ...

    ## Insert widgets for the Footer Dialog Box ('horizontal_layout')
    start_button_text = 'Start'
    self.start_button = QtWidgets.QPushButton(start_button_text, self)
    self.start_button.clicked.connect(self.on_button_click)
    horizontal_layout.addWidget(self.start_button)
    horizontal_layout.addStretch(1)
    # ...
    # ... other widgets ...
    # ...

    vertical_layout.addLayout(horizontal_layout)
    self.setLayout(vertical_layout)


def on_update_progressbar(self, value):

    self.DIALOG.progress_bar.setValue(value)


def on_emit_exception(self, value):

    """
    Quit the threads and close the installation dialog.
    """

    # ## Terminate Thread
    if self.DIALOG.jobthread.isRunning():
        self.DIALOG.jobthread.terminate()

    message = "There was an error: %s" % str(value)
    if hasattr(value, "url"):
        message += " (%s)." % value.url
    else:
        message += "."
    message += " Quitting the Process."
    print(message)
    ##self.tab.show_error_message("Installation Error", message)

    self.DIALOG.close()


def on_update_progress_text(self, text):

    '''
    Get signal to update the text
    '''

    self.DIALOG.initial_label.setText(text)


def on_process_completed(self, func):

    '''
    Get signal to close dialog, stop thread and run final step.
    '''

    # ## Close Dialog
    self.DIALOG.close()

    ## Update with results
    func()

    ## Terminate Thread
    if self.DIALOG.jobthread.isRunning():
        self.DIALOG.jobthread.terminate()

################################## CODE-BLOCK 1 ###############################################################


class DialogThread(_dialog_mixin, QtWidgets.QDialog): #### 3.

    """
    The DialogThread object represent the Dialog from which the Thread is run.
    It must: initialized (__init__) and setup (setup_thread)
             see how to do it in 'initDialog' function.

    """

    def __init__(self, main):

        self.main = main
        QtWidgets.QDialog.__init__(self, parent=self.tab)


    def setup_thread(self, starting_function):

        ### 3a. Initialize Job
        self.jobthread = JobThread(self)
        ### 3b. Setup parameters
        self.jobthread.set_params(self, self.main, starting_function)


    def on_button_click(self):

        ### 3a. Run Job
        self.jobthread.start()
        self.setWindowTitle('In process. Please wait ...')
        self.start_button.setEnabled(False)

    def close_dialog_prior_process(self):

        self._terminate_threads()
        self.close()

    def _terminate_threads(self):
        if self.jobthread.isRunning():
            self.jobthread.terminate()

    def closeEvent(self, evnt):
        self._terminate_threads()
        self.close()


class JobThread(QtCore.QThread): #### 4.

    """
    The JobThread object represent the Job run as a Thread, it is a QtCore.QThread like object.
    """

    def __init__(self, tab):
        super().__init__(tab)

    ### 4a. Define the signals (QtCore.pyqtSignal)
    ###   - The QtCore.pyqtSignal takes as input the Type of the signal (i.e. Python Data Types)
    ###   - The variables storing the desired signal are called in the Step ### 2c.
    ###   - QtCore.pyqtSignal have the 'connect' method to be called with the desired function to be connected to the signal as input
    emit_exception = QtCore.pyqtSignal(Exception)
    update_progress_text = QtCore.pyqtSignal(str)
    process_completed = QtCore.pyqtSignal()
    update_progressbar = QtCore.pyqtSignal(int)


    def set_params(self, dialog, tab, main, starting_function):

        ### 4b. Setup parameters about the main parent class, the dialog and the function to be called when running the process.
        self.dialog = dialog
        self.main = main
        self.starting_function = starting_function


    @catch_errors_installer_threads
    def run(self):

        self.starting_function()
