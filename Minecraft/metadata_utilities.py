import os
import json
import colorsys

import networkx
from networkx.algorithms.components.connected import connected_components
from networkx.readwrite import json_graph

from itertools import combinations
import operator

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


def node_strength(node):
    return sum(np.array(node.edges(data=True))[:, 2])


def connectivity_sort(network, threshold=1):
    """Returns each bunch sub-ordered by connectivity"""

    connectivity_net = []

    for bunch in connected_components(network):
        connectivity_net.append(sorted(bunch, key=node_strength))

    return [i for i in connectivity_net if len(i) > threshold]


def network_images(raster_dict, threshold=0, network=None):

    if network is None:
        network = networkx.Graph()

    new_elements = set(raster_dict.keys()) - set(network.nodes())
    network.add_nodes_from(new_elements)

    def center(nodes):
        bunch_build = {}
        for point in nodes:
            bunch_build[point] = network.degree(point)
        return max(bunch_build.items(), key=operator.itemgetter(1))[0]

    for group_outer, group_inner in combinations(connected_components(network), 2):
        correlation = analyze.correlate(raster_dict[center(group_outer)], raster_dict[center(group_inner)])

        if correlation > threshold:
            # print("Matched: " + str(node_outer[0]) + ' & ' + str(node_inner[0]))
            network.add_edge(center(group_inner), center(group_outer), weight=correlation)

    # Name each bunch
    for bunch in connected_components(network):
        max(bunch, key=node_strength)

        name = None
        for node in bunch:
            if node.name is not None:
                name = node.name

        if name is None:
            name = max(np.vectorize(node_strength)(bunch)).name

        for node in bunch:
            network[node]['name'] = name

    # for group in connected_components(network):
    #     if len(group) > 1:
    #         for node in group:
    #             print(node)
    #         print(" ")

    return network


def template_metadata(template_directory, image_graph, raster_dict, sections=10):
    keys = {}
    for bunch in connected_components(image_graph):
        for node in bunch:
            keys[node] = (node.name, raster_dict[node])
            layer_map = analyze.cluster(raster_dict[node], 10)
            image_clusters, guide = filter.merge_similar(*filter.layer_decomposite(raster_dict[node], layer_map))
            

    return keys


def file_metadata(output_directory, template_directory, keys, sections=10):
    """Save representative data to json files in meta pack"""

    for key, (template_name, default_image) in keys.items():
        # print(key, template_name)

        output_path = os.path.split(output_directory + key)[0]

        layer_map = analyze.cluster(default_image, 4)
        image_clusters, guide = filter.merge_similar(*filter.layer_decomposite(default_image, layer_map))

        template_path = template_directory + '\\' + template_name

        template_components = []
        for image_name in os.listdir(template_path):
            template_components.append(Raster.from_path(template_path + '\\' + image_name))

        segment_metalist = []
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
