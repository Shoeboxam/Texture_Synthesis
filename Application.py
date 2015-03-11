from settings import *
from file_utilities import *
from image_utilities import *

from shutil import rmtree


def create_default():
    """Creates a default texture pack in mod repository format"""

    temp_pack = home + "\\resourcepacks\\temp\\"

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


def image_analysis():
    """Extract representative colors for every image that matches template"""
    template_index = list_templates(template_path)
    keys = identify_templates(default_pack, template_path, threshold=.85)
