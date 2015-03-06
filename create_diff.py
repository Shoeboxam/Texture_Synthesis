import os
from os.path import join
from shutil import copytree

def untextured_paths(resource_pack, default_pack):
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
