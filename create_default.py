import zipfile
import os
from distutils.dir_util import copy_tree
import shutil


def remove_cruft(target_path):
    # Filter out all filetypes that are not .png
    for root, folders, files in os.walk(target_path, topdown=False):
        for current_file in files:
            if not current_file.endswith('.png'):
                try:
                    os.remove(os.path.join(root, current_file))
                except FileNotFoundError:
                    print("Skipping deletion of " + os.path.join(root, current_file))

        for current_folder in folders:
            folder_name = root + "\\" + current_folder
            if not os.listdir(folder_name):
                os.rmdir(folder_name)


def make_default(home, separate=True):
    for file in os.listdir(home + "\\mods\\"):
        if file.endswith(".jar"):
            try:
                zip_ob = zipfile.ZipFile(home + "\\mods\\" + file)

                mod_path = home + "\\resourcepacks\\temp\\"
                if (separate):
                    mod_path += ("\\" + file)

                try:
                    zip_ob.extractall(mod_path)
                except PermissionError:
                    print("Skipped " + file + " [PermissionError]")
                except FileNotFoundError:
                    pass

                try:
                    os.rename(mod_path, home + "\\resourcepacks\\temp\\" + os.listdir(mod_path + "\\assets")[0])
                except FileNotFoundError:
                    print("Skipping rename of " + file + " [FileNotFoundError]")
                    shutil.rmtree(mod_path)
                except FileExistsError:
                    copy_tree(mod_path, home + "\\resourcepacks\\temp\\" + os.listdir(mod_path + "\\assets")[0])
                    shutil.rmtree(mod_path)

                print(file)

            finally:
                # Remove lock
                zip_ob.close()


def extract_matches(source, output, key_repository):

    asset_dictionary = {}
    for folder in os.listdir(key_repository):
        try:
            asset_dictionary[folder] = os.listdir(key_repository + '//' + folder + '//assets')[0]
        except FileNotFoundError:
            pass  # Ignore nonstandard and .git folders

    for k, v in asset_dictionary.items():
        if v in os.listdir(source):
            copy_tree(source + "\\" + v, output + "\\" + k)
