import json

from Minecraft.file_utilities import extract_files, resource_filter, repository_format, get_untextured, copytree_wrapper
from Minecraft.image_utilities import template_detect, build_metadata_tree, populate_images
from Minecraft.web_utilities import clone_repo

from shutil import rmtree

from os.path import normpath, expanduser

config = json.load(open("./config.json"))
home = normpath(expanduser(config['home']))

resource_pack = home + '\\resource_pack\\'
mods_directory = home + "\\mods\\"
template_directory = home + '\\templates\\'
diff_pack = home + '\\default_diff\\'
metadata_pack = home + '\\default_metadata\\'
output_path = home + '\\synthesized_resources\\'
default_pack = home + '\\default\\'
key_repository = home + '\\key_repository\\'


def main():
    setup_environment()
    # create_default()
    # create_diff()
    # image_synthesis()


def setup_environment():
    clone_repo(config['resource_pack'], resource_pack)
    clone_repo(config['key_repository'], key_repository)


def create_default():
    """Creates a default texture pack in mod repository format"""

    temp_pack = home + "\\resource_temp\\"

    # Create staging pack
    extract_files(mods_directory, temp_pack)
    resource_filter(temp_pack)

    # Convert to repo format and output to default pack path
    repository_format(temp_pack, default_pack, key_repository)

    # Delete staging pack
    rmtree(temp_pack, True)


def create_diff():
    """Creates a pack of untextured files in mod repository format"""

    # Gets a list of textures that have not been made via file diff
    untextured_paths = get_untextured(resource_pack, default_pack)

    # Create a pack with the untextured files
    copytree_wrapper(default_pack, diff_pack, untextured_paths)
    resource_filter(diff_pack)


def image_synthesis():
    """Extract representative colors for every image that matches template"""

    keys = template_detect(diff_pack, template_directory, threshold=.85)

    # # print(json.dumps(keys))

    keyfile = open('keyfile.txt', 'r')
    keyfile.write(json.dumps(keys) + "\n")

    # keys = json.loads(keyfile.readline())
    # print(keys)
    build_metadata_tree(diff_pack, metadata_pack, keys, 5)

    # Converts json files to images with templates
    populate_images(template_directory, metadata_pack, output_path)


if __name__ == "__main__":
    main()
