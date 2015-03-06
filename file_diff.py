import os
from os.path import join
from shutil import copytree
from make_default.py import remove_cruft

resource_pack = 'C:\\Users\mike_000\Textures\Modded-1.7.x\\'
default_pack = 'C:\\Users\mike_000\AppData\Roaming\.ftb\FTBInfinity\minecraft\\resourcepacks\default\\'

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
    if not(name in resource_listing.keys()):
        untextured_paths.append(name)

untextured_paths.sort()
untextured_paths = [os.path.normpath(default_pack + p) for p in untextured_paths]
print(untextured_paths)

def keep_list(folder, files):

    ignore_list = []
    for file in files:
        full_path = os.path.join(folder, file)
        if not os.path.isdir(full_path):
            if full_path not in untextured_paths:
                ignore_list.append(file)
    return ignore_list

diff_pack = default_pack.replace("resourcepacks\default", "resourcepacks\default_diff")
copytree(default_pack, diff_pack, ignore=keep_list)

# Remove extra files and folders from diff using make_default.py
remove_cruft(diff_pack)