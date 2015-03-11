import zipfile
import os
from distutils.dir_util import copy_tree

from shutil import copytree
from shutil import rmtree


def resource_filter(target_path):
    """Filter out all filetypes that are not .png"""

    # Walk file tree from tips, deleting non png files, then empty folders
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


def extract_files(mods_directory, staging_directory, separate=True):
    """Unzip every mod into staging directory"""

    for file in os.listdir(mods_directory):
        if file.endswith(".jar"):
            try:
                zip_ob = zipfile.ZipFile(mods_directory + file)

                mod_path = staging_directory
                if (separate):
                    mod_path += ("\\" + file)

                # Extract mod into staging directory
                try:
                    zip_ob.extractall(mod_path)
                except PermissionError:
                    print("Skipped " + file + " [PermissionError]")
                except FileNotFoundError:
                    pass

                # Rename mod folder to the name of its assets folder, merging shared folders
                try:
                    os.rename(mod_path, staging_directory + os.listdir(mod_path + "\\assets")[0])
                except FileNotFoundError:
                    print("Skipping rename of " + file + " [FileNotFoundError]")
                    rmtree(mod_path)
                except FileExistsError:
                    copy_tree(mod_path, staging_directory + os.listdir(mod_path + "\\assets")[0])
                    rmtree(mod_path)

            finally:
                # Remove lock
                zip_ob.close()


def repository_format(source, output, key_repository):
    """Convert texture pack to repository format """

    # Link asset folder name to mod name in key repository
    asset_dictionary = {}
    for folder in os.listdir(key_repository):
        try:
            asset_dictionary[folder] = os.listdir(key_repository + '//' + folder + '//assets')[0]
        except FileNotFoundError:
            pass  # Ignore nonstandard and .git folders

    # Use asset-modname link to identify mods via their asset folder names
    for k, v in asset_dictionary.items():
        if v in os.listdir(source):
            copy_tree(source + "\\" + v, output + "\\" + k)


def get_untextured(resource_pack, default_pack):
    """Returns list of paths that are in default_pack, but not in resource_pack """

    # Create list of relative texture paths for every file in resource pack
    resource_listing = {}
    for root, dirs, files in os.walk(resource_pack):
        for name in files:
            path = os.path.join(root, name).replace(resource_pack, "")
            resource_listing[path] = 1

    # Create list of relative texture paths for every file in default pack
    default_listing = {}
    for root, dirs, files in os.walk(default_pack):
        for name in files:
            path = os.path.join(root, name).replace(default_pack, "")
            default_listing[path] = 1

    # Differentiate listings to find untextured files
    untextured_paths = []
    for name in default_listing.keys():
        if not(name in resource_listing.keys()) and not name.startswith("\\.git"):
            untextured_paths.append(name)

    # Sort paths to cluster images near each other in directory tree, for readability
    return untextured_paths.sort()


def copytree_wrapper(default_pack, diff_pack, untextured_paths):
    """Copy untextured files from default pack into new directory """

    # Copytree passes list of files it plans to copy
    # keep_list returns a list of files that have been textured (to ignore)
    def keep_list(folder, files):
        ignore_list = []
        for file in files:
            full_path = os.path.join(folder, file)
            if not os.path.isdir(full_path):
                if os.path.normpath(full_path.replace(default_pack, "")) not in untextured_paths:
                    ignore_list.append(file)
        return ignore_list

    copytree(default_pack, diff_pack, ignore=keep_list)
