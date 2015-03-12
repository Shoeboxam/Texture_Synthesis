from PIL import Image
from scipy.stats.stats import pearsonr
from sklearn.cluster import KMeans
import numpy as np

import os
import json


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
    """Save representative data to json files in meta pack"""

    for key, template_name in image_keys.items():

        key_path = analysis_directory + key
        output_path = os.path.split(output_directory + key)[0]

        # Calculate colors from image in analysis_directory
        representative_colors = color_extract(3, key_path).tolist()

        # Create folder structure
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Save json file
        with open(output_path + "\\" + os.path.split(key)[1] + ".json", 'w') as output_file:
            json.dump([template_name, representative_colors], output_file)


def load_pixels(path):
    """Load path to pixel array"""

    subject_image = Image.open(path)
    subject_image = subject_image.convert("RGBA")

    # Convert to numpy array
    return np.asarray(subject_image.getdata())


def color_extract(color_count, target_image):
    """Pass in image path, returns X number of representative colors"""

    pixels = load_pixels(target_image)

    # Retrieve opaque pixels
    pixel_list = []
    for index in range(len(pixels)):

        if pixels[index][3] > 0:
            pixel_list.append(pixels[index])

    # Calculate X number of representative colors deterministically
    KMeans_object = KMeans(n_clusters=color_count, random_state=0)
    return KMeans_object.fit(pixel_list).cluster_centers_
