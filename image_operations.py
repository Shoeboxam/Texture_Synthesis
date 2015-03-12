import os
from PIL import Image
import json
import math
import numpy as np

np.set_printoptions(threshold=np.nan)

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


def image_decompose(source, layers):
    """Slice image by a given number of lightness zones"""

    master_mask_image = source.convert("L")
    width, height = source.size

    # Convert to numpy array, then normalize to range of opacity variables
    master_mask = np.asarray(master_mask_image).astype(float).flatten() / 256
    master_mask_range = master_mask.max() - master_mask.min()

    # Create linearly-spaced value based layer masks spread over range of source image lightness
    mask_list = []
    opacity_range = master_mask_range / layers

    for current_layer in range(layers):
        pixels_mask = []

        # Peak opacity = lowest opacity + spacers + 50% offset
        opacity_peak = master_mask.min() + (opacity_range * current_layer) + (opacity_range / 2)

        for lightness in master_mask:
            # If lightness is within mask's opacity period...
            if lightness > opacity_peak - (opacity_range / 2) and lightness < opacity_peak + (opacity_range / 2):

                # Resolve edge case to preserve transparency in low and high lightness
                if lightness < master_mask.min() + opacity_range / 2 or lightness > master_mask.max() - opacity_range / 2:
                    pixels_mask.append(1)
                else:
                    # ... then weight opacity sinusoidally- two adjacent layers have inverse opacities, therefore preserving original value
                    pixels_mask.append(math.cos(2 * math.pi * lightness - 2 * math.pi * opacity_peak) / 2 + .5)

            else:
                # Avoid opacity contamination from periodicity in cosine
                pixels_mask.append(0)

        # Reformat pixel list into rows and columns, then into image
        pixels_mask = np.reshape(pixels_mask, (width, height))

        mask_list.append(Image.fromarray(pixels_mask))

    # Apply all transparency masks to source image
    layer_list = []
    for mask in mask_list:
        mask = np.asarray(mask).reshape(width * height)
        source_pixels = np.asarray(source).reshape(width * height, 4)

        source_pixels.flags.writeable = True

        source_pixels[:, 3] = mask * 256
        masked_source_pixels = np.reshape(source_pixels, (width, height, 4))
        print(masked_source_pixels)

        layer_list.append(Image.fromarray(masked_source_pixels, mode='RGBA'))

    return layer_list


def image_compose(layers):
    canvas = layers[0]
    for index in range(1, len(layers) - 1):
        canvas = Image.alpha_composite(canvas, layers[index + 1])
    return canvas


def populate_images(templates_path, metadata_pack, output_path):
    list_templates(templates_path)
    for root, folders, files in os.walk(metadata_pack):
        for file in files:
            full_path = os.path.join(root, file)


image_list = image_decompose(Image.open(r"C:\Users\mike_000\Desktop\pack.png"), 2)

for num, image in enumerate(image_list):
    image.save(r"C:\Users\mike_000\Desktop\\" + str(num) + ".png")