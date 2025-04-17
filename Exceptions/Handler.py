
import sys
import traceback

from PyQt5.QtWidgets import QMessageBox


def handle_exception(exc_type, exc_value, exc_traceback):
    traceback_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Critical)
    msgBox.setText(str(exc_value))
    msgBox.setWindowTitle(exc_type.__name__)
    msgBox.setDetailedText(traceback_details)
    msgBox.exec_()


def connect():
    sys.excepthook = handle_exception
