from PIL import Image
from scipy.stats.stats import pearsonr
from sklearn.cluster import KMeans
from skimage import io
import numpy as np

import os
import json
import colorsys


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


def correlate(template, candidate):
    """Returns statistical correlation between two lists"""

    if (template.size != candidate.size):
        return 0

    return pearsonr(template, candidate)[0]


def template_detect(target, template_path, threshold):
    """Finds all occurences of templates in target directory"""

    def brightnesses(path):
        """Convert from path to list of values"""
        image_input = Image.open(path)
        return image_input.convert("L").getdata()

    # Load template images into variables
    image_keys = {}
    template_filenames = os.listdir(template_path + "\\keys\\")
    template_images = []
    for filename in template_filenames:
        template_images.append(brightnesses(template_path + "\\keys\\" + filename))

    # Check every file against every template
    for root, folders, files in os.walk(target):
        for current_file in files:
            full_path = root + "\\" + current_file

            # template with highest correlation is selected
            highest_correlation = [0, "null"]
            for template_pixels, template_filename in zip(template_images, template_filenames):
                relation_coefficient = correlate(template_pixels, brightnesses(full_path))

                if relation_coefficient > highest_correlation[0]:
                    highest_correlation = [relation_coefficient, template_filename]

            if highest_correlation[0] > threshold:
                image_keys[full_path.replace(target, "")] = highest_correlation[1]

    return image_keys


def build_metadata_tree(analysis_directory, output_directory, image_keys):
    """Produce json meta files for every image in key"""
    for key in image_keys.keys():

        # Calculate colors from image in analysis_directory
        key_path = os.path.join(analysis_directory, key)
        representative_colors = color_extract(3, key_path)

        # Save colors to json file in meta pack
        output_path = os.path.join(output_directory, key)
        with open(output_path, 'w') as output_file:
            json.dump(representative_colors, output_file)


def color_extract(color_count, target_image):
    """Pass in image path, returns X number of representative colors"""

    # Image load into numpy array- list of lines of pixels of channels
    subject_image = io.imread(target_image)

    # Flatten into a list of pixels of channels
    width, height, depth = tuple(subject_image.shape)
    image_array = np.reshape(subject_image, (width * height, depth))

    # KMeans.fit(image), where KMeans calcs X colors deterministically
    return KMeans(n_clusters=color_count, random_state=0).fit(image_array).cluster_centers_
