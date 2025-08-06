""" 
Assignment 3 - Batch Renamer Script with GUI
Maysam Al-Ani
Created: 3/3/2025

"""

import os
import shutil

class BatchRenamer:
    def __init__(
        self,
        filepath=None,
        copy_files=False,
        filetypes=None,
        strings_to_find=None,
        string_to_replace="",
        prefix=None,
        suffix=None,
    ):
        self.filepath = filepath
        self.copy_files = copy_files
        self.filetypes = filetypes
        self.strings_to_find = strings_to_find
        self.string_to_replace = string_to_replace
        self.prefix = prefix
        self.suffix = suffix

    def get_renamed_file_path(
        self, existing_name, string_to_find, string_to_replace, prefix, suffix
    ):

        # Seperating basename and extension from existing_name
        basename, extension = os.path.splitext(existing_name)

        # Ensure string_to_find is a list for iteration consistency
        if isinstance(string_to_find, str):
            string_to_find = [string_to_find]


        # Replace occurrences of string_to_find in basename
        for find in string_to_find:
            if find in basename:
                print(
                    f"Trying to replace '{find}' in '{basename}' \
                        with '{string_to_replace}'"
                )
            else:
                print(f"'{find}' NOT found in '{basename}'")

            basename = basename.replace(find, string_to_replace)
        print(f"Basename after replacement: '{basename}'")

        # Construct the new name
        new_name = f"{prefix}{basename}{suffix}{extension}"

        return new_name

    def get_files_with_extension(self, filepath, extension):

        matched_files = []

        if not os.path.isdir(filepath):
            print(f"ERROR: The assigned folder path does not exist: {filepath}")
            return []

        print(f"Scanning folder '{filepath}' for extension: '{extension}'")

        # Normalize: remove leading dot and lowercase it
        extension = extension.lstrip(".").lower()
        print(extension)

        for filename in os.listdir(filepath):
            file_path = os.path.join(filepath, filename)

            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename)
                ext = ext.lower().lstrip(".")

                if ext == extension:
                    matched_files.append(filename)

        print(f"Matched files: {matched_files}")
        return matched_files


    def rename_file(self, existing_name, new_name, copy=False):

        existing_name = os.path.join(self.filepath, existing_name)
        new_name = os.path.join(self.filepath, new_name)

        # If the file path does not exist, throw an error, 
        # otherwise proceeed to try and copy/rename
        if not os.path.exists(existing_name):
            print(f"ERROR:File not found: {existing_name}")
        else:
            print(f"File found: {existing_name} in folder")

        try:
            # if copy = True, shutil.copy file
            if copy:
                shutil.copy(existing_name, new_name)
                print(f"Copied file: {existing_name} to {new_name}")
                return
            # if copy = False, os.rename file
            else:
                os.rename(existing_name, new_name)
                print(f"Renamed file {existing_name} to {new_name}")

        # A write permission error may arise, 
        # This lets it be known and attempts to fix it. If unsuccessful, quits.
        except PermissionError as e:
            print(f"ERROR copying file: {existing_name} to {e}")

        try:
            os.chmod(new_name, 0o755)
            print("Permissions fixed successfully! \
                             Resuming procedure")

        except OSError as e:
            print(
                f"ERROR changing permissions: {e} \n Will now stop trying!"
            )

        return (
            new_name and existing_name
        )  # returns these values to be used in a later def

    def rename_files_in_folder(
        self,
        filepath,
        extension,
        string_to_find,
        string_to_replace,
        prefix,
        suffix,
        copy_files=False,
    ):
        files = self.get_files_with_extension(filepath, extension)

        renamed_files = set()
        copied_files = set()
        errored_files = set()
        target_files = set()
        extension_error = False

        if not extension:
            print("ERROR: No extension was provided")
            extension_error = True
            return target_files, None, renamed_files, copied_files, errored_files, extension_error

        if not files:
            print(f"ERROR: No files with extension '{extension}' were found in the folder.")
            extension_error = True
            return target_files, extension, renamed_files, copied_files, errored_files, extension_error

        target_files.update(files)

        print(f"Working on renaming these files: {', '.join(target_files)} with extension: '{extension}'")

        for filename in files:
            existing_path = os.path.join(filepath, filename)

            new_name = self.get_renamed_file_path(
                filename, string_to_find, string_to_replace, prefix, suffix
            )
            new_path = os.path.join(filepath, new_name)

            if filename == new_name:
                print(f"DEBUG: No match found in '{existing_path}'")
                errored_files.add(existing_path)
                continue

            try:
                if copy_files:
                    shutil.copy(existing_path, new_path)
                    print(f"Copied file: {existing_path} → {new_path}")
                    copied_files.add(new_path)
                else:
                    os.rename(existing_path, new_path)
                    print(f"Renamed file: {existing_path} → {new_path}")
                    renamed_files.add(new_path)
            except Exception as e:
                print(f"ERROR renaming/copying '{existing_path}': {e}")
                errored_files.add(existing_path)

        return target_files, extension, renamed_files, copied_files, errored_files, extension_error

