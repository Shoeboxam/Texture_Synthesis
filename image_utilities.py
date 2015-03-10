from PIL import Image
from scipy.stats.stats import pearsonr
from sklearn.cluster import KMeans
from skimage import io
import numpy as np

import os
import csv
import colorsys

from settings import *


# Applies (filter/function) to all images in directory
def analyze(target, function, *args):
    for root, folder, file, in os.walk(target):
        image_path = os.path.join(root, file)
        image_class = Image.open(image_path)
        image_raw = image_class.getdata()

        image_raw_hsv = [colorsys.rgb_to_hsv(color) for color in image_raw]

        KMeans(n_clusters=3)


# Unused, likely to be removed
def meta_info(image_path):
    meta_dict = {}
    image_class = Image.open(image_path)
    image_raw = image_class.getdata()

    image_raw_hsv = [colorsys.rgb_to_hsv(*color[0:3]) for color in image_raw]
    KMeans_var = KMeans(init='k-means++', n_clusters=3, n_init=10)
    meta_dict["RGB_Set"] = KMeans_var.fit(image_raw)
    print(meta_dict["RGB_Set"])

    # meta_dict["hue"] = KMeans(n_clusters=3, data=zip(*image_raw_hsv)[0])
    # meta_dict["saturation"] = KMeans(n_clusters=3, data=zip(*image_raw_hsv)[1])
    # meta_dict["value"] = KMeans(n_clusters=3, data=zip(*image_raw_hsv)[2])


    return 


def color_extract(color_count, target_image):
    # Image load into numpy array- list of lines of pixels of channels
    subject_image = io.imread(target_image)

    # Flatten into a list of pixels of channels
    width, height, depth = tuple(subject_image.shape)
    image_array = np.reshape(subject_image, (width * height, depth))

    # KMeans.fit(image), where KMeans calcs X colors deterministically
    return KMeans(n_clusters=color_count, random_state=0).fit(image_array).cluster_centers_


def resize(tile, scalar):
    return tile.resize(tile.size*scalar)


def create_template_index(template_path):
    matches = []
    keys = os.listdir(template_path + '\\keys\\')
    values = os.listdir(template_path + '\\values\\')

    for filename_default, filename_replacer in zip(keys, values):
        if (filename_default == filename_replacer):
            matches.append(filename_default)
        else:
            print("Incomplete template pairing: " + filename_default)

    return matches


# Convert from path to brightness list
def pixelate(path):
    image_input = Image.open(path)
    return image_input.convert("L").getdata()


# Template must already be in list format- performance optimization
def correlate(template, candidate):

    if (template.size != candidate.size):
        return 0

    # This number is... magic!
    threshold = .85
    return threshold < abs(pearsonr(template, candidate)[0])


def create_identification_dictionary(target, template_path):
    # Load template images into variables
    image_keys = {}

    template_filenames = os.listdir(template_path + "\\keys\\")

    template_images = []
    for filename in template_filenames:
        template_images.append(pixelate(template_path + "\\keys\\" + filename))

    for root, folders, files in os.walk(target):
        for current_file in files:
            full_path = root + "\\" + current_file

            for temp_pixels, temp_filename in zip(template_images, template_filenames):
                if correlate(temp_pixels, pixelate(full_path)):
                    image_keys[full_path.replace(target, "")] = temp_filename

    return image_keys


def texture_synthesize():
    template_index = create_template_index(template_path)
    keys = create_identification_dictionary(default_pack, template_path)
    colors = color_extract(3, r"C:\Users\mike_000\Textures\Modded-1.7.x\Minefactory_Reloaded\assets\minefactoryreloaded\textures\blocks\tile.mfr.machineblock.prc.png")
    print(colors)