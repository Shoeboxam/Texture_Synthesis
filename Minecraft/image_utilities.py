import os
import json
import colorsys

import networkx
from networkx.algorithms.components.connected import connected_components
from networkx.readwrite import json_graph

from itertools import combinations
import operator

from shutil import copy

from Raster.Raster import Raster
from Raster import filter, math_utilities, analyze

import numpy as np


def load_graph(path):
    try:
        json_data = open(path, 'r')
    except FileNotFoundError:
        return None
    return json_graph.node_link_graph(eval(json_data.read()))


def save_graph(path, graph):
    json_file = open(path, 'w')
    json_file.write(str(json_graph.node_link_data(graph)))


def load_directory(target):
    raster_dict = {}
    for root, folders, files in os.walk(target):
        for current_file in files:
            full_path = root + "\\" + current_file
            candidate = Raster.from_path(full_path, 'RGBA')
            raster_dict[full_path.replace(target, "")] = candidate

    return raster_dict


def get_templates(network, threshold=1):
    """Returns most connected node of each bunch"""

    template_list = []
    for bunch in connected_components(network):
        degree_vec = np.vectorize(network.degree)

        node_rankings = zip(bunch, degree_vec(bunch))
        template, rank = max(node_rankings, key=operator.itemgetter(1))

        if rank >= threshold:
            template_list.append(template)

    return template_list


def template_extract(raster_dict, threshold=0, network=None):

    if network is None:
        network = networkx.Graph()

    new_elements = set(raster_dict.keys()) - set(network.nodes())
    network.add_nodes_from(new_elements)

    def center(nodes):
        bunch = {}
        for point in nodes:
            bunch[point] = network.degree(point)
        return max(bunch.items(), key=operator.itemgetter(1))[0]

    for group_outer, group_inner in combinations(connected_components(network), 2):
        correlation = analyze.correlate(raster_dict[center(group_outer)], raster_dict[center(group_inner)])

        if correlation > threshold:
            # print("Matched: " + str(node_outer[0]) + ' & ' + str(node_inner[0]))
            network.add_edge(group_inner[0], group_outer[0], weight=correlation)

    # for group in connected_components(network):
    #     if len(group) > 1:
    #         for node in group:
    #             print(node)
    #         print(" ")

    return network


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
    '''Uses the image graph to create a dict of targets'''
    split_vec = np.vectorize(os.path.split)
    image_keys_list = zip(np.array(split_vec(template_paths))[:, 1], connected_components(image_graph))

    image_keys = {}

    for template, targets in image_keys_list:
        for node in targets:
            image_keys[template] = node

    return image_keys


def build_metadata_tree(analysis_directory, output_directory, template_directory, keys, sections):
    """Save representative data to json files in meta pack"""

    for key, template_name in keys.items():
        # print(key, template_name)

        output_path = os.path.split(output_directory + key)[0]
        img = Raster.from_path(analysis_directory + key, 'RGBA')

        layer_map = analyze.cluster(img, 4)
        image_clusters, guide = filter.merge_similar(*filter.layer_decomposite(img, layer_map))

        segment_metalist = []

        template_components = []
        template_path = template_directory + '\\' + template_name
        for image_name in os.listdir(template_path):
            template_components.append(Raster.from_path(template_path + '\\' + image_name))

        for segment, template_segment in image_clusters, template_components:
            segment_metalist.append(analyze_image(segment, template_segment, sections))

        meta_dict = {
            'segment_dicts': json.dumps(segment_metalist),
            'cluster_map': guide
        }

        # Create folder structure
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Save json file
        with open(output_path + "\\" + os.path.split(key)[1] + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file)


def analyze_image(image, template, granularity):
    equivalent = False
    if np.array_equal(image.get_opaque(), template.get_opaque()):
        equivalent = True

    colors = analyze.color_extract(image, granularity)[:, 3]

    hues = []
    sats = []
    vals = []

    for color in colors:
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hues.append(h)
        sats.append(s)
        vals.append(v)

    hues = math_utilities.circular_sort(hues)
    sats = sorted(sats)[::-1]
    vals = sorted(vals)

    data_variance = analyze.variance(image, 'V')
    lightness = analyze.mean(image, 'V')

    return {
        'template': template.name,
        'apply': equivalent,
        'hues': hues,
        'sats': sats,
        'vals': vals,
        'lightness': lightness,
        'variance': data_variance}


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
    # Split into clusters
    pieces = filter.layer_decomposite(image, json_data['cluster_map'])

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
