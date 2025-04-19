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

        # Creating lists for each file/extension type
        ma_files = []
        txt_files = []
        png_files = []
        extension = []

        # Check if the folder_path exists and has been found, else errors out
        if os.path.isdir(filepath) is True:

            print(
                f"The assigned folder path has been found and exists: \
                      {filepath}"
            )
            files = os.listdir(filepath)

        else:
            print(
                f"ERROR:The assigned folder path has NOT been found \
                    and does not exist. Folder path: {filepath}"
            )
            return []

        # List out all the files within filepath
        files = os.listdir(filepath)

        # Construct a file path 
        # & then split the name between basename & filetype
        for existing_name in files:
            file_path = os.path.join(filepath, existing_name)
            if os.path.isfile(file_path):
                basename, filetype = os.path.splitext(existing_name)

            # Sort files based on extensions
            if filetype == ".ma":
                ma_files.append(existing_name)
                if filetype not in extension:
                    extension.append(filetype)

            elif filetype == ".png":
                png_files.append(existing_name)
                if filetype not in extension:
                    extension.append(filetype)

            elif filetype == ".txt":
                txt_files.append(existing_name)
                if filetype not in extension:
                    extension.append(filetype)
            # If none of the above [.ma, .png, .txt], 
            # then throw a warning message in the print
            else:
                print(
                    f"ERROR:The file {existing_name} extension type does not match \
                          the provided extensions {extension}, \
                            and thus is not applicable."
                )

        return (
            ma_files,
            png_files,
            txt_files,
            filepath,
        )  # return to be used in later defs

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
        """
        Renames all files in a folder with a given extension
        This should operate only on files with the provided extension
        Every instance of string_to_find in the filepath should be replaced
        with string_to_replace
        Prefix should be added to the front of the file name
        Suffix should be added to the end of the file name

        Args:
            folder_path: the path to the folder the renamed files are in
            extension: the extension of the files you'd like renamed
            string_to_find: the string in the filename you'd like to replace
            string_to_replace: the string you'd like to replace it with
            prefix: a string to insert at the beginning of the file path
            suffix: a string to append to the end of the file path
            copy: whether to rename/move the file or duplicate/copy it
        """

        """
        REMINDERS
        #
        This function should:
            - Find all files in a folder that use a certain extension
                - Use get_files_with_extension for this
            - *For each* file...
                - Determine its new file path
                    - Use get_renamed_file_path for this
                - Rename or copy the file to the new path
                    - Use rename_file for this
        """

        # To use to find all files in folder that use a certain extension
        files = BatchRenamer.get_files_with_extension(self, 
                                                      filepath, 
                                                      extension)

        # Setting these to be stored for front-end use
        renamed_files = set()
        copied_files = set()
        errored_files = set()
        target_files = set()
        extension_error = False

        # If no extension provided, store error
        if not extension:
            print("ERROR:No extension was provided")
            extension_error = True
            return (
                target_files,
                None,
                renamed_files,
                copied_files,
                errored_files,
                extension_error,
            )

        # If extension is provided, look for it in the filepath
        print(f"Scanning folder: {filepath} for .{extension} files")

        # 'Flattening' nested list that came from get_files_with_extension
        files_fix_nested_list = [item for sublist in files for item in 
                                 (sublist if isinstance(sublist, list) 
                                  else [sublist])]

        # Check if the filenames in the list end with the provided extension
        # If it does, add it to target_files.
        # If not, log error and add it to extension_error.
        for filename in files_fix_nested_list:
            if (isinstance(filename, str) and 
                filename.endswith(f".{extension}")):
                target_files.add(filename)
        if not target_files:
            print(
                f"ERROR:No files with extension '{extension}' \
                    were found in the folder."
            )
            extension_error = True
            return (
                target_files,
                extension,
                renamed_files,
                copied_files,
                errored_files,
                extension_error,
            )

        print(
            f"Working on renaming these files: '{', '.join(target_files)}' \
                with the provided extension: '{extension}'"
        )

        # For the files in the filepath -
        # use os.walk to dynamically get files to avoid already renamed files
        #
        for root, _, files in os.walk(filepath):  # Dynamically get files
            for filename in files:
                if not filename.endswith(f".{extension}"):
                    continue  # Skip files that don't match extension

                existing_name = os.path.join(root, filename)

                new_name = self.get_renamed_file_path(
                    filename, string_to_find, string_to_replace, prefix, suffix
                )
                new_path = os.path.join(root, new_name)

                if filename == new_name:  # Skip if the name remains unchanged
                    print(
                        f"DEBUG: No match found in '{existing_name}'"
                    )  # <-- Check if this prints
                    errored_files.add(existing_name)
                    continue

                try:
                    if copy_files:
                        shutil.copy(existing_name, new_path)
                        print(f"Copied file: {existing_name} to \
                                         {new_path}")
                        copied_files.add(new_path)
                    else:
                        os.rename(existing_name, new_path)
                        print(f"Renamed file: {existing_name} to \
                                         {new_path}")
                        renamed_files.add(new_path)  # Track renamed file
                except Exception as e:
                    print(f"ERROR renaming '{existing_name}': {e}")
                    errored_files.add(existing_name)  # Mark as errored

        return (
            target_files,
            extension,
            renamed_files,
            copied_files,
            errored_files,
            extension_error,
        )  # Return proper tracking
