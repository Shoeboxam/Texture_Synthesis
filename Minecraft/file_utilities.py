import zipfile
import os
from distutils.dir_util import copy_tree

from shutil import rmtree, copy2


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


def copy_filter(source_directory, output_directory, paths_to_copy):
    """Copy untextured files from default pack into new directory"""

    # keep_list returns a list of files that have been textured (to ignore)
    def keep_list(folder, files):
        ignore_list = []
        for file_name in files:
            full_path = os.path.join(folder, file_name)
            if not os.path.isdir(full_path):
                if os.path.normpath(full_path.replace(source_directory, "")) not in paths_to_copy:
                    ignore_list.append(file_name)
        return ignore_list

    def copytree(src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                copytree(s, d, symlinks, ignore)
            else:
                if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                    copy2(s, d)

    copytree(source_directory, output_directory, ignore=keep_list)


def extract_files(mods_directory, staging_directory, separate=True):
    """Unzip every mod into staging directory"""

    if not os.path.exists(staging_directory):
        os.makedirs(staging_directory)

    for file_name in os.listdir(mods_directory):
        if file_name.endswith(".jar"):
            try:
                zip_ob = zipfile.ZipFile(mods_directory + file_name)

                mod_path = staging_directory
                if separate:
                    mod_path += ("\\" + file_name)

                # Extract mod into staging directory
                try:
                    zip_ob.extractall(mod_path)
                except PermissionError:
                    print("Skipped " + file_name + " [PermissionError]")
                except:
                    pass

                # Rename mod folder to the name of its assets folder, merging shared folders
                try:
                    target_folder = staging_directory + os.listdir(mod_path + "\\assets")[0]
                except FileNotFoundError:
                    continue

                try:
                    os.rename(mod_path, target_folder)
                # Mod naming intuition
                except FileNotFoundError:
                    rmtree(mod_path)
                except FileExistsError:
                    copy_tree(mod_path, target_folder)
                    rmtree(mod_path)
                except PermissionError:
                    pass

            finally:
                # Remove lock
                zip_ob.close()


def repository_format(source, output, key_repository):
    """Convert texture pack to repository format"""

    if not os.path.exists(output):
        os.makedirs(output)

    # Link asset folder name to mod name in key repository
    asset_dictionary = {}
    for folder in os.listdir(key_repository):
        try:
            asset_dictionary[folder] = os.listdir(key_repository + '//' + folder + '//assets')
        except FileNotFoundError:
            pass  # Ignore nonstandard and .git folders

    # Use asset-modname link to identify mods via their asset folder names
    for k, v in asset_dictionary.items():
        for subfolder in v:
            if subfolder in os.listdir(source):
                copy_tree(source + "\\" + subfolder, output + "\\" + k)


def get_untextured(resource_pack, default_pack):
    """Returns list of paths that are in default_pack, but not in resource_pack """

    # Create list of relative texture paths for every file in resource pack
    resource_listing = {}
    for root, dirs, files in os.walk(resource_pack):
        for name in files:
            path = str(os.path.join(root, name)).replace(resource_pack, "")
            resource_listing[path] = 1

    # Create list of relative texture paths for every file in default pack
    default_listing = {}
    for root, dirs, files in os.walk(default_pack):
        for name in files:
            path = str(os.path.join(root, name)).replace(default_pack, "")
            default_listing[path] = 1

    # Differentiate listings to find untextured files
    untextured_paths = []
    for name in default_listing.keys():
        if not(name in resource_listing.keys()) and not name.startswith("\\.git"):
            untextured_paths.append(name)

    # Sort paths to cluster images near each other in directory tree, for readability
    return untextured_paths.sort()
