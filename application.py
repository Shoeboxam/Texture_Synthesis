from create_default import *
from create_diff import *
from create_mappings import *
from settings import *

# from batch_apply import *


def create_default():
    shutil.rmtree(home + "\\resourcepacks\\temp\\", True)

    make_default(home)
    remove_cruft(home + "\\resourcepacks\\temp\\")
    extract_matches(home + "\\resourcepacks\\temp\\", home + "\\resourcepacks\\default\\", key_repository)

    shutil.rmtree(home + "\\resourcepacks\\temp\\", True)


def create_diff():
    untextured_paths = untextured_paths(resource_pack, default_pack)
    copytree_wrapper(default_pack, diff_pack, untextured_paths)

    # Remove extra files and folders from diff using make_default.py
    remove_cruft(diff_pack)


def texture_synthesize():
    template_index = create_template_index(template_path)
    keys = create_identification_dictionary(diff_pack, template_path)

    print(keys)


texture_synthesize()
