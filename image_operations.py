import os
from PIL import Image, ImageOps
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

    master_mask_image = source.convert("L")
    width, height = source.size
    source_alpha = np.asarray(source).reshape((width * height, 4))[:, 3]

    # Convert to numpy array, then normalize to range of opacity variables
    master_mask = np.asarray(master_mask_image).astype(float).flatten() / 255

    master_mask_range = master_mask.max() - master_mask.min()

    # Create linearly-spaced value based layer masks spread over range of source image lightness
    mask_list = []
    opacity_range = master_mask_range / layers
    omega = (2 * math.pi) / opacity_range

    for current_layer in range(layers):
        pixels_mask = []

        # Peak opacity = lowest opacity + spacers - 50% offset
        opacity_peak = master_mask.min() + (opacity_range * current_layer) + (opacity_range / 2)
        phase_shift = master_mask.min() + opacity_range/2 + opacity_range * current_layer

        for lightness in master_mask:
            # If lightness is within mask's opacity period...
            if (opacity_peak - (opacity_range / 2) <= lightness <= opacity_peak + (opacity_range / 2)):
                # Resolve edge case to preserve transparency in low and high lightness
                if master_mask.min() + opacity_range / 2 <= lightness <= master_mask.max() - opacity_range / 2:
                    # ... then weight opacity sinusoidally- two adjacent layers have inverse opacities, therefore preserving original value
                    pixels_mask.append(math.cos(omega * lightness - phase_shift * opacity_range) / 2 + .5)
                else:
                    pixels_mask.append(1)
            else:
                pixels_mask.append(0)

        pixels_mask_filtered = []
        for lightness, alpha in zip(pixels_mask, source_alpha):
            if alpha == 0:
                pixels_mask_filtered.append(0)
            else:
                pixels_mask_filtered.append(lightness)

        # Reformat pixel list into rows and columns, then into image
        pixels_mask = np.reshape(pixels_mask_filtered, (width, height))
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
    pixel_layers = np.asarray([np.asarray(layer) for layer in layers])

    width, height = layers[0].size
    canvas = np.zeros((width, height, 4))

    for channel in range(2):
        canvas[channel] = np.average(pixel_layers[:, channel], weights=pixel_layers[:, 3])

    canvas[3] = np.clip(np.sum(pixel_layers[:, 3]), 0, 255)

    pixels = (np.array(canvas) * 255).astype(int)
    pixels = np.reshape(pixels, (width, height, 4))
    return Image.fromarray(canvas, mode='RGBA')


def colorize(image, color, opacity=1):
    width, height = image.size
    channels_rgb = np.asarray(image).reshape(width * height, 4).astype(float)

    color = [c / 255 for c in color]
    target_hue, target_sat, target_value = colorsys.rgb_to_hsv(*color[:3])

    pixels_rgb_output = []
    for r, g, b, a in channels_rgb:
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        if a != 0:
            # print(h, s, a)
            # print(target_hue, target_sat)
            h = (target_hue * opacity) + h * (1 / opacity)
            s = (target_sat * opacity) + s * (1 / opacity)
            # print(h, s)

        red, green, blue = colorsys.hsv_to_rgb(h, s, v)
        pixels_rgb_output.append([red, green, blue, a])

    pixels = (np.array(pixels_rgb_output)).astype(np.uint8)
    pixels = np.reshape(pixels, (width, height, 4))
    print(np.array(Image.fromarray(pixels, mode='RGBA')))
    return Image.fromarray(np.ascontiguousarray(pixels), mode='RGBA')

    # np.average(pixels_hsv[:, 0])


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

                colorized_layers = []
                for index, layer in enumerate(layers):
                    # layer.save('C:\Users\mike_000\Desktop\\' + str(index) + ".png")
                    colorized_layers.append(colorize(layer, json_data["colors"][index], .9))

                # Debug
                for index, layer in enumerate(colorized_layers):
                    layer.save('C:\Users\mike_000\Desktop\\' + str(index) + ".png")

                output_image = image_composite(colorized_layers)
                output_image = light_adjust(output_image, np.average(json_data["colors", :]))

                full_path_output = full_path.replace(metadata_pack, output_path).replace(".json", "")

                if not os.path.exists(os.path.basename(full_path_output)):
                    os.path.makedirs(os.path.basename(full_path_output))

                output_image.save(full_path_output)
