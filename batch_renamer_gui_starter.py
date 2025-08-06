""" 
Assignment 3 - Batch Renamer Script with GUI
Maysam Al-Ani
Created: 3/3/2025

"""

import sys
import os
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

#Importing UI
from batch_renamer_ui import Ui_MainWindow

#Importing backend script
import batch_renamer_lib
from batch_renamer_lib import BatchRenamer


class BatchRenamerWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # UI Setup
        super().__init__()
        super(Ui_MainWindow).__init__()
        self.setupUi(self)
        # Connect button to function
        self.browseBtn.clicked.connect(self.get_filepath)
        self.runBtn.clicked.connect(self.run_renamer)
        self.error_dialog = QtWidgets.QErrorMessage(self)
        self.info_dialog = QMessageBox(self)

        # Instance the "back end"
        self.batch_renamer = batch_renamer_lib.BatchRenamer()

        # Show UI normal vs maximized
        self.showNormal()

    def get_filepath(self):
        """
        Open a file dialog for browsing to a folder
        """
        selected_path = QFileDialog().getExistingDirectory()
        if selected_path:  # Ensure the user selected a folder
            self.filepath = selected_path
            self.set_filepath()
        else:
            self.error_dialog.showMessage("Warning: No folder selected!")

    def set_filepath(self):
        """
        Set lineEdit text for filepath
        """
        self.filepathEdit.setText(self.filepath)
        self.update_list()

    def update_list(self):
        """
        Clear listwidget
        read files in filepath with os.walk
        Add files as new items
        """
        self.listWidget.clear()
        for root, dirs, files in os.walk(self.filepath):
            self.listWidget.addItems(files)

    def get_parameters(self):

        # Check if renameRB or copyRB is checked
        # if renameRB is checked, set value for rename_mode
        # if copyRB is checked, set value for copy_mode
        self.rename_mode = self.renameRB.isChecked()
        self.copy_mode = self.copyRB.isChecked()

        # if rename_mode, make copy_mode false
        if self.rename_mode == True:
            self.copy_mode = False

        # if copy_mode, make rename_mode false
        elif self.copy_mode == True:
            self.rename_mode = False

        # Find string_to_find in the text line edit, make it a list
        self.string_to_find = self.string_to_findEdit.text()
        if isinstance(self.string_to_find, (str, tuple)):
            self.string_to_find = list(self.string_to_find)

        self.string_to_find_list = [
            s.strip() for s in self.string_to_findEdit.text().split(",")
        ]

        # Sort the list by length so that the long strings are found first
        # Helps to avoid immediate string replace for similar strings
        # i.e. "tex" and "texture"
        self.string_to_find_list.sort(key=len, reverse=True)
        print(self.string_to_find_list)

        self.string_to_replace = self.string_to_replaceEdit.text().strip()

        return (
            self.rename_mode,
            self.copy_mode,
            self.string_to_find,
            self.string_to_replace,
            self.string_to_find_list,
        )

    # Function to gather and set parameters based upon UI
    def run_renamer(self):
        """
        Run back end batch renamer using self.batch_renamer
        self.batch_renamer is an instance of the BatchRenamer class
        """
        self.batch_renamer.filepath = self.filepath

        if self.batch_renamer.filepath == None:
            self.error_dialog.showMessage("Cannot run operation: no filepath \
                                          was provided!")
            print("ERROR:No filepath provided, cannot run")
            return        

        # Get parameters from UI
        (
            self.rename_mode,
            self.copy_mode,
            self.string_to_find,
            self.string_to_replace,
            self.string_to_find_list,
        ) = self.get_parameters()

        extension = self.filetypesEdit.text()
        extension = extension.lstrip(".").lower()
        print(f"Extension entered: '{extension}'")


        # Rename via batch_renamer_lib if rename_mode = True
        if self.rename_mode:
            (
                target_files,
                extension,
                renamed_files,
                copied_files,
                errored_files,
                extension_error,
            ) = self.batch_renamer.rename_files_in_folder(
                filepath=self.filepath,
                extension=extension,
                string_to_find=self.string_to_find_list,
                string_to_replace=self.string_to_replaceEdit.text(),
                prefix=self.prefixEdit.text(),
                suffix=self.suffixEdit.text(),
                copy_files=False,
            )

        # Copy via batch_renamer_lib if copy_mode = True
        elif self.copy_mode:
            (
                target_files,
                extension,
                renamed_files,
                copied_files,
                errored_files,
                extension_error,
            ) = self.batch_renamer.rename_files_in_folder(
                filepath=self.filepath,
                extension=extension,
                string_to_find=self.string_to_find_list,
                string_to_replace=self.string_to_replaceEdit.text(),
                prefix=self.prefixEdit.text(),
                suffix=self.suffixEdit.text(),
                copy_files=True,
            )

        # Set up and show error/success messages
        # Shortening by splitting full paths
        message = []
        short_names_original = [
            filename.split("\\")[-1] for filename in target_files]
        short_names_copied = [
            filename.split("\\")[-1] for filename in copied_files]
        short_names_renamed = [
            filename.split("\\")[-1] for filename in renamed_files]
        short_names_errored = [
            filename.split("\\")[-1] for filename in errored_files]

        # Different messages depending on the different outcomes
        # (copied, renamed, errored (string or extension error))

        if copied_files:
            message.append(
                f"Successfully copied files {", ".join(short_names_original)} \
                    to {", ".join([repr(name) for name in copied_files])}."
            )
        if renamed_files:
            message.append(
                f"Successfully renamed files \
                    {", ".join([repr(name) 
                                for name in short_names_original])} \
                          to {", ".join([repr(name) 
                                         for name in short_names_renamed])}."
            )

        if errored_files:
            message.append(
                f"Failed to rename/copy these files: \
                    {", ".join(short_names_errored)}. \
                        They did not contain {self.string_to_find_list}."
            )

        if extension_error:
            message.append(
                f"Failed to find files with the provided extension: \
                    '{extension}'"
            )

        if message:  # Only show dialog if there's something to report
            self.error_dialog.showMessage("\n".join(message))

        self.update_list()

        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BatchRenamerWindow()
    sys.exit(app.exec())
