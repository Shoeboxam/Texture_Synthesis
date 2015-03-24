from PIL import Image
from scipy.stats.stats import pearsonr
import numpy as np

import os
import json
import colorsys


def correlate(template, candidate):
    """Returns correlation coefficient between two pixel lists"""

    if (template.size != candidate.size):
        return 0

    width, height = template.size
    template_pixels = np.asarray(template).reshape((width * height, 4))
    candidate_pixels = np.asarray(candidate.convert('RGBA')).reshape((width * height, 4))

    template_pixels_value = [colorsys.rgb_to_hsv(*pixel[:3])[2] for pixel in template_pixels]
    candidate_pixels_value = [colorsys.rgb_to_hsv(*pixel[:3])[2] for pixel in candidate_pixels]

    coefficient_rgb = pearsonr(template_pixels_value, candidate_pixels_value)[0]

    # Calculate alpha relation independently to avoid contamination with colors
    coefficient_alpha = pearsonr(template_pixels[:, 3], candidate_pixels[:, 3])[0]
    if coefficient_alpha < .99:
        return 0

    return coefficient_rgb


def template_detect(target, template_path, threshold):
    """Finds all occurences of templates in target directory"""

    # Load template images into variables
    image_keys = {}
    template_filenames = os.listdir(template_path + "\\keys\\")
    template_images = []
    for filename in template_filenames:
        template_images.append(Image.open(template_path + "\\keys\\" + filename))

    # Check every file against every template
    for root, folders, files in os.walk(target):
        for current_file in files:
            full_path = root + "\\" + current_file

            # template with highest correlation is selected
            highest_correlation = [0, "null"]
            for template_pixels, template_filename in zip(template_images, template_filenames):
                relation_coefficient = correlate(template_pixels, Image.open(full_path))

                if relation_coefficient > highest_correlation[0]:
                    highest_correlation = [relation_coefficient, template_filename]

            if highest_correlation[0] > threshold:
                print(highest_correlation)
                image_keys[full_path.replace(target, "")] = highest_correlation[1]

    return image_keys


def build_metadata_tree(analysis_directory, output_directory, image_keys, sections):
    """Save representative data to json files in meta pack"""

    for key, template_name in image_keys.items():

        key_path = analysis_directory + key
        output_path = os.path.split(output_directory + key)[0]

        # Calculate colors from image in analysis_directory
        representative_colors = color_extract(sections, key_path).tolist()

        # Create folder structure
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        lightness = 0
        variance = 0

        meta_dict = {
            'template': template_name,
            'colors': representative_colors,
            'lightness': lightness,
            'variance': variance}

        # Save json file
        with open(output_path + "\\" + os.path.split(key)[1] + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file)


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


def populate_images(templates_path, metadata_pack, output_path):

    for root, folders, files in os.walk(metadata_pack):
        for file in files:
            full_path = os.path.join(root, file)

            with open(full_path, 'r') as json_file:
                json_data = json.load(json_file)

                template = Image.open(templates_path + "\\values\\" + json_data["template"])
                source_pixels = np.asarray(template).reshape((width * height, 4))

                layer_count = len(json_data["colors"])
                source_pixel_layers = image_decompose(source_pixels, layer_count)

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