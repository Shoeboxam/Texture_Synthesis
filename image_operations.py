import os
from PIL import Image
import json


def list_templates(template_path):
    """Returns a list of names of key-value template image pairs"""
    matches = []
    keys = os.listdir(template_path + '\\keys\\')
    values = os.listdir(template_path + '\\values\\')

    for filename_default, filename_replacer in zip(keys, values):
        if (filename_default == filename_replacer):
            matches.append(filename_default)
        else:
            print("Incomplete template pairing: " + filename_default)

    return matches


# Applies (filter/function) to all images in directory
def batch_apply(target, function, *args):
    for root, folder, file in os.walk(target):
        current_image = Image.open(os.path.join(root, file))
        current_image = function(current_image, *args)
        current_image.save(os.path.join(root, file))


def resize(tile, scalar):
    return tile.resize(tile.size*scalar)


def populate_images(templates_path, metadata_pack, output_path):
    list_templates(templates_path)
    for root, folders, files in os.walk(metadata_pack):
        for file in files:
            full_path = os.path.join(root, file)
            
