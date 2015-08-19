import os
import json
from networkx.algorithms.components.connected import connected_components

from shutil import copy

from Raster.Raster import Raster
from Raster import filter, math_utilities, analyze

import numpy as np
np.set_printoptions(precision=2, linewidth=1000)


def prepare_templates(default_pack, resource_pack, path_list, template_directory):
    if not os.path.exists(template_directory):
        os.mkdir(template_directory)
        os.mkdir(template_directory + '\\default\\')
        os.mkdir(template_directory + '\\resource\\')

    for path in path_list:
        if os.path.exists(resource_pack + path):
            copy(default_pack + path, template_directory + '\\default\\' + os.path.split(path)[1])
            copy(resource_pack + path, template_directory + '\\resource\\' + os.path.split(path)[1])


def template_reader(template_paths, image_graph):
    """Uses the image graph to create a dict of targets"""
    split_vec = np.vectorize(os.path.split)
    image_keys_list = zip(np.array(split_vec(template_paths))[:, 1], connected_components(image_graph))

    image_keys = {}

    for template, targets in image_keys_list:
        for node in targets:
            image_keys[template] = node

    print(image_keys)
    return image_keys


def best_match(graph, resource_pack):
    template_listing = []

    def best_existing(bunch_examine):
        for node in bunch_examine:
            if os.path.exists(resource_pack + '\\' + node):
                return node
        return None

    for bunch in graph:
        match = best_existing(bunch)
        if match is not None:
            template_listing.append(match)

    return template_listing


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


def populate_images(source_files, template_directory, metadata_pack, output_path):

    for root, folders, files in os.walk(metadata_pack):
        for image_file in files:
            full_path = os.path.join(root, image_file)

            with open(full_path, 'r') as json_file:

                # Open data sources
                try:
                    json_data = json.load(json_file)
                    template_json_data = json.load(
                        template_directory + '//' + os.path.split(json_data['group_name'])[1] + '.json')
                    template = Raster.from_path(source_files + '//' + json_data['group_name'], 'RGBA')
                except IOError:
                    print('IOError: skipping map')
                    continue

                # Transform image
                output_image = apply_template(template, json_data, template_json_data)

                # Output/save image
                full_path_output = full_path.replace(metadata_pack, output_path).replace('.json', '')

                if not os.path.exists(os.path.split(full_path_output)[0]):
                    os.makedirs(os.path.split(full_path_output)[0])

                output_image.get_image().save(full_path_output)


def apply_template(image, json_data, template_json_data):
    # Split into clusters
    pieces = filter.layer_decomposite(image, template_json_data['cluster_map'])

    altered_pieces = []
    for segment, cluster_data in zip(pieces, json_data['segment_dicts']):

        if cluster_data['apply']:
            # Adjust contrast
            contrast_mult = (analyze.variance(segment, 'V') - cluster_data['variance']) * .3
            staged_image = filter.contrast(segment, contrast_mult)

            # Adjust lightness
            lightness_adjustment = cluster_data['lightness'] - analyze.mean(segment, 'V')
            staged_image = filter.brightness(staged_image, lightness_adjustment)

            # Adjust coloration
            layer_count = len(cluster_data['hues'])*2
            components = filter.value_decomposite(staged_image, layer_count)

            sat_poly_raw = math_utilities.polyfit(np.linspace(0, 1, len(cluster_data['sats'])), cluster_data['sats'])

            sorted_hues = math_utilities.circular_sort(cluster_data['hues'])
            linear_mapped_hues = (np.array(sorted_hues) - sorted_hues[0]) % 1
            hue_poly = math_utilities.polyfit(np.linspace(0, 1, len(cluster_data['hues'])), linear_mapped_hues)

            colorized_components = []
            for index, layer in enumerate(components):

                normalized_index = float(index) / len(components)

                hue_target = (math_utilities.polysolve(hue_poly, normalized_index) + sorted_hues[0]) % 1
                sat_target = math_utilities.polysolve(sat_poly_raw, normalized_index)

                # Reduce sat in lighter areas of image
                sat_target -= pow(2, (-5 * normalized_index)) / 2 - .05

                layer = filter.colorize(layer, hue_target, sat_target, 0, 1., 1., 0.0)
                colorized_components.append(layer)

            staged_image = filter.composite(colorized_components)

        else:
            staged_image = segment

        altered_pieces.append(staged_image)

    return filter.composite(altered_pieces)
