import zipfile
import os
from distutils.dir_util import copy_tree

from shutil import copytree
from settings import *


def extract_defaults():
    vanilla_dir = home + "\\resourcepacks\\default_vanilla\\"
    zip_ob = ZipFile(jar_path)

    zip_ob.extractall(vanilla_dir)

    # Remove lock
    zip_ob.close()
    remove_cruft(vanilla_dir)


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


def get_untextured(resource_pack, default_pack):
    resource_listing = {}
    for root, dirs, files in os.walk(resource_pack):
        for name in files:
            path = os.path.join(root, name).replace(resource_pack, "")
            resource_listing[path] = 1

    default_listing = {}
    for root, dirs, files in os.walk(default_pack):
        for name in files:
            path = os.path.join(root, name).replace(default_pack, "")
            default_listing[path] = 1

    untextured_paths = []
    for name in default_listing.keys():
        if not(name in resource_listing.keys()) and not name.startswith("\\.git"):
            untextured_paths.append(name)

    untextured_paths.sort()
    return untextured_paths


def copytree_wrapper(default_pack, diff_pack, untextured_paths):
    def keep_list(folder, files):
        ignore_list = []
        for file in files:
            full_path = os.path.join(folder, file)
            if not os.path.isdir(full_path):
                if os.path.normpath(full_path.replace(default_pack, "")) not in untextured_paths:
                    ignore_list.append(file)
        return ignore_list

    copytree(default_pack, diff_pack, ignore=keep_list)


def create_default():
    shutil.rmtree(home + "\\resourcepacks\\temp\\", True)

    make_default(home)
    remove_cruft(home + "\\resourcepacks\\temp\\")
    extract_matches(home + "\\resourcepacks\\temp\\", home + "\\resourcepacks\\default\\", key_repository)

    shutil.rmtree(home + "\\resourcepacks\\temp\\", True)


def create_diff():
    untextured_paths = get_untextured(resource_pack, default_pack)
    copytree_wrapper(default_pack, diff_pack, untextured_paths)

    # Remove extra files and folders from diff using make_default.py
    remove_cruft(diff_pack)
