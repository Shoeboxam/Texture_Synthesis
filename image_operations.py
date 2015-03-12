import os
from PIL import Image
import PIL.ImageOps
import json
import math
import np


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


def template_decompose(template, layers):

    master_mask = template.convert("L")

    opacity_range = 1 / layers
    for current_layer in range(layers):
        pixels_mask = []
        opacity_peak = opacity_range * current_layer - (opacity_range / 2)
        for lightness in np.asarray(master_mask)[0]:
            # If lightness is within first period
            if lightness > opacity_peak - (opacity_range / 2) and lightness < opacity_peak + (opacity_range / 2):
                # Then weight opacity sinusoidally
                pixels_mask.append(math.cos(2 * math.pi * lightness - 2 * math.pi * opacity_peak) / 2 + .5)
            else:
                pixels_mask.append(0)

        width, height = template.size

        Image.fromarray(np.reshape(pixels_mask, width, height))

        Image.alpha_composite()


def populate_images(templates_path, metadata_pack, output_path):
    list_templates(templates_path)
    for root, folders, files in os.walk(metadata_pack):
        for file in files:
            full_path = os.path.join(root, file)
