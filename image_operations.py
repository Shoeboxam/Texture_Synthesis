import collections

import os
from PIL import Image
import json
import math
import numpy as np
import colorsys

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

    pixels_rgb_output = []
    min_lightness = 255

    width, height = source.size

    source_pixels = np.asarray(source).reshape((width * height, 4))
    for r, g, b, a in source_pixels:
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        if a != 0 and v < min_lightness:
            min_lightness = v

    min_lightness /= 255.
    print(min_lightness)

    # Convert to numpy array, then normalize to 1
    master_mask = np.asarray(source.convert("L")).astype(float).flatten() / 255

    master_mask_range = master_mask.max() - min_lightness

    # Create linearly-spaced value based layer masks spread over range of source image lightness
    mask_list = []
    layer_range = master_mask_range / layers
    period = (2 * math.pi) / layer_range

    for current_layer in range(layers):
        print(current_layer)
        pixels_mask = []

        horizontal_translation = min_lightness + layer_range * current_layer + layer_range / 2

        print(str(horizontal_translation - (layer_range)) + " - " + str(horizontal_translation + (layer_range)))
        conversion_tracker = {}
        for lightness in master_mask:
            # If lightness is within mask's first period...
            if (horizontal_translation - layer_range <= lightness <= horizontal_translation + layer_range):
                # Resolve edge case to preserve transparency in low and high lightness
                if min_lightness + layer_range / 2 <= lightness <= master_mask.max() - layer_range / 2:
                    # ... then weight opacity sinusoidally- two adjacent layers have inverse opacities, therefore preserving original value
                    pixels_mask.append(math.cos(period * (lightness - horizontal_translation)) / 2 + .5)
                    conversion_tracker[float(lightness)] = str(math.cos(period * (lightness - horizontal_translation)) / 2 + .5)
                else:
                    pixels_mask.append(1)
            else:
                pixels_mask.append(0)
        print(collections.OrderedDict(conversion_tracker))

        # Reformat pixel list into rows and columns, then into image
        pixels_mask = np.reshape(pixels_mask, (width, height))
        mask_list.append(Image.fromarray(pixels_mask))

    # Apply all transparency masks to copies of source image
    layer_list = []
    for mask in mask_list:
        mask = np.asarray(mask).reshape(width * height)
        source_pixels = np.asarray(source).reshape(width * height, 4)

        source_pixels.flags.writeable = True

        # Replace alpha channel with normalized mask. Take ceil to prevent truncation of weak pixels
        source_pixels[:, 3] = np.ceil(mask * 255)
        masked_source_pixels = np.reshape(source_pixels, (width, height, 4))

        layer_list.append(Image.fromarray(masked_source_pixels, mode='RGBA'))

    return layer_list


def image_composite(layers):
    """Combine all input layers with additive alpha blending"""

    # Break image list into list of pixel lists
    width, height = layers[0].size
    pixel_layers = np.asarray([np.asarray(layer).reshape(width * height, 4) for layer in layers])

    # Results for each pixel is added to canvas
    canvas = []

    # Take transpose of pixel layers to produce a list of pixels in identical positions
    for pixel_list in np.array(zip(*pixel_layers)):

        # Opacity is the sum of alpha channels
        # TODO: Unit test this:
        opacity = sum(pixel_list[:, 0])
        print(pixel_list[:, 3])

        # If one of the pixels has opacity
        if opacity != 0:
            pixel = []

            # Calculate weights for each pixel's colors based on alpha strength between 0 and 1
            opacity_weight_sum = pixel_list[:, 3].sum()
            normalized_opacity_weights = pixel_list[:, 3] / opacity_weight_sum

            # Multiply channel values with their weights, then add together
            pixel.append((pixel_list[:, 0] * normalized_opacity_weights).sum())
            pixel.append((pixel_list[:, 1] * normalized_opacity_weights).sum())
            pixel.append((pixel_list[:, 2] * normalized_opacity_weights).sum())
            pixel.append(opacity)
            canvas.append(pixel)
        else:
            canvas.append([0, 0, 0, 0])

    pixels = (np.array(canvas)).astype(np.uint8)
    pixels = np.reshape(pixels, (width, height, 4))
    return Image.fromarray(np.ascontiguousarray(pixels), mode='RGBA')


def colorize(image, color, opacity=1):
    width, height = image.size
    channels_rgb = np.asarray(image).reshape(width * height, 4).astype(float)

    color = [c / 255 for c in color]
    target_hue, target_sat, target_value = colorsys.rgb_to_hsv(*color[:3])

    pixels_rgb_output = []
    for r, g, b, a in channels_rgb:
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        if a != 0:
            h = (target_hue * opacity) + h * (1 / opacity)
            s = (target_sat * opacity) + s * (1 / opacity)

        red, green, blue = colorsys.hsv_to_rgb(h, s, v)
        pixels_rgb_output.append([red, green, blue, a])

    pixels = (np.array(pixels_rgb_output)).astype(np.uint8)
    pixels = np.reshape(pixels, (width, height, 4))
    output_image = Image.fromarray(np.ascontiguousarray(pixels), mode='RGBA')

    return output_image


def light_adjust(image, lightness, opacity=1):

    return image


def populate_images(templates_path, metadata_pack, output_path):

    for root, folders, files in os.walk(metadata_pack):
        for file in files:
            full_path = os.path.join(root, file)
            print(full_path)
            with open(full_path, 'r') as json_file:
                json_data = json.load(json_file)

                template = Image.open(templates_path + "\\values\\" + json_data["template"])
                layer_count = len(json_data["colors"])
                layers = image_decompose(template, layer_count)

                for index, layer in enumerate(layers):
                    layer.save('C:\Users\mike_000\Desktop\\' + str(index) + ".png")

                colorized_layers = []
                for index, layer in enumerate(layers):
                    colorized_layers.append(colorize(layer, json_data["colors"][index], .9))

                output_image = image_composite(colorized_layers)
                output_image = light_adjust(output_image, np.average(json_data["colors"]))

                full_path_output = full_path.replace(metadata_pack, output_path).replace(".json", "")

                if not os.path.exists(os.path.split(full_path_output)[0]):
                    os.makedirs(os.path.split(full_path_output)[0])

                output_image.save(full_path_output)
                output_image.save('C:\Users\mike_000\Desktop\\' + "test2" + ".png")
                1/0
                
