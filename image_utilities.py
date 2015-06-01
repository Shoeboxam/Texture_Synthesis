import os
import json
import colorsys

from raster.raster import Raster
from raster.analyze import correlate, color_extract, variance, mean
from raster.filter import brightness, contrast, colorize, value_decomposite, composite
from utility.modular_math import circular_sort


def template_detect(target, template_path, threshold):
    """Finds all occurrences of templates in target directory"""

    # Load template images into variables
    image_keys = {}
    template_filenames = os.listdir(template_path + "\\keys\\")
    template_images = []
    for filename in template_filenames:
        template_images.append(Raster.from_path(template_path + "\\keys\\" + filename))

    # Check every file against every template
    for root, folders, files in os.walk(target):
        for current_file in files:
            full_path = root + "\\" + current_file
            candidate = Raster.from_path(full_path)
            # template with highest correlation is selected
            highest_correlation = [0, "null"]
            for template, template_filename in zip(template_images, template_filenames):
                correlation = correlate(template, candidate)

                if correlation > highest_correlation[0]:
                    highest_correlation = [correlation, template_filename]

            if highest_correlation[0] > threshold:
                image_keys[full_path.replace(target, "")] = highest_correlation[1]

    return image_keys


def build_metadata_tree(analysis_directory, output_directory, image_keys, sections):
    """Save representative data to json files in meta pack"""

    for key, template_name in image_keys.items():
        # print(key, template_name)

        output_path = os.path.split(output_directory + key)[0]
        img = Raster.from_path(analysis_directory + key, 'RGBA')

        # Calculate colors from image in analysis_directory
        colors = color_extract(img, sections)[:, :3]

        hues = []
        sats = []
        vals = []

        for color in colors:
            r, g, b = color
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hues.append(h)
            sats.append(s)
            vals.append(v)

        hues = circular_sort(hues)
        sats = sorted(sats)[::-1]
        vals = sorted(vals)

        # print(sorted_hues, sats, vals)

        data_variance = variance(img, 'V')
        lightness = mean(img, 'V')

        # Create folder structure
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        meta_dict = {
            'template': template_name,
            'hues': hues,
            'sats': sats,
            'vals': vals,
            'lightness': lightness,
            'variance': data_variance}

        # Save json file
        with open(output_path + "\\" + os.path.split(key)[1] + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file)


def list_templates(template_path):
    """Returns a list of names of key-value template image pairs"""
    matches = []
    keys = os.listdir(template_path + '\\keys\\')
    values = os.listdir(template_path + '\\values\\')

    for filename_default, filename_replacer in zip(keys, values):
        if filename_default == filename_replacer:
            matches.append(filename_default)
        else:
            print("Incomplete template pairing: " + filename_default)

    return matches


def populate_images(templates_path, metadata_pack, output_path):

    for root, folders, files in os.walk(metadata_pack):
        for image_file in files:
            full_path = os.path.join(root, image_file)

            with open(full_path, 'r') as json_file:

                # Open data sources
                try:
                    json_data = json.load(json_file)
                    template = Raster.from_path(templates_path + '\\values\\' + json_data['template'], 'RGBA')
                except IOError:
                    continue

                # Transform image
                output_image = apply_template(template, json_data)

                # Output/save image
                full_path_output = full_path.replace(metadata_pack, output_path).replace('.json', '')

                if not os.path.exists(os.path.split(full_path_output)[0]):
                    os.makedirs(os.path.split(full_path_output)[0])

                output_image.get_image().save(full_path_output)


def apply_template(image, json_data):
    # Adjust contrast
    contrast_mult = (variance(image, 'V') - json_data['variance']) * .3
    image = contrast(image, contrast_mult)

    # Adjust lightness
    lightness_adjustment = json_data['lightness'] - mean(image, 'V')
    image = brightness(image, lightness_adjustment)

    # Adjust coloration
    layer_count = len(json_data['hues'])
    components = value_decomposite(image, layer_count)

    colorized_components = []
    for index, layer in enumerate(components):
        layer = colorize(layer, json_data['hues'][index], json_data['sats'][index], 0, 1., 1., 0.0)
        colorized_components.append(layer)

    return composite(colorized_components)
