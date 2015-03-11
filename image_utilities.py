from PIL import Image
from scipy.stats.stats import pearsonr
from sklearn.cluster import KMeans
from skimage import io
import numpy as np

import os
import csv
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


def identify_templates(target, template_path, threshold):
    """Produces dictionary of paths as keys and template detected as value"""

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

            for temp_pixels, temp_filename in zip(template_images, template_filenames):
                if threshold < correlate(temp_pixels, brightnesses(full_path)):
                    image_keys[full_path.replace(target, "")] = temp_filename

    return image_keys


def color_extract(color_count, target_image):
    """Pass in image path, returns X number of representative colors"""

    # Image load into numpy array- list of lines of pixels of channels
    subject_image = io.imread(target_image)

    # Flatten into a list of pixels of channels
    width, height, depth = tuple(subject_image.shape)
    image_array = np.reshape(subject_image, (width * height, depth))

    # KMeans.fit(image), where KMeans calcs X colors deterministically
    return KMeans(n_clusters=color_count, random_state=0).fit(image_array).cluster_centers_
