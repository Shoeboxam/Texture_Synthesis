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
            name = max(np.vectorize(node_strength)(bunch))

        for node in bunch:
            network[node]['name'] = name

    # for group in connected_components(network):
    #     if len(group) > 1:
    #         for node in group:
    #             print(node)
    #         print(" ")

    return network


def template_metadata(template_directory, image_graph, raster_dict, sections=10):
    """Generate spectral cluster maps for the templates"""

    for bunch in connected_components(image_graph):

        template_name = os.path.split(bunch[0].name)[1]
        template_image = raster_dict[bunch[0].name]

        # Clustering algorithm
        layer_map = analyze.cluster(template_image, sections)
        image_clusters, guide = filter.merge_similar(*filter.layer_decomposite(template_image, layer_map))

        # Analyze each cluster, save to list of dicts
        segment_metalist = []
        for segment, template_segment in image_clusters:
            segment_metalist.append(analyze_image(segment, sections))

        meta_dict = {
            'group_name': template_name,
            'segment_dicts': json.dumps(segment_metalist),
            'cluster_map': guide
        }

        # Create folder structure
        if not os.path.exists(template_directory):
            os.makedirs(template_directory)

        # Save json file
        with open(template_directory + "\\meta\\" + os.path.split(template_name)[1] + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file)


def file_metadata(output_directory, template_directory, raster_dict, image_graph, sections=10):
    """Save representative data to json files in meta pack"""

    template_metadata = {}
    for json_filename in os.listdir(template_directory + '\\meta\\'):
        with open(template_directory + '\\meta\\' + json_filename, 'r') as json_file:
            json_data = json.load(json_file)
            template_metadata[json_data['group_name']] = json_data

    # Retrieve the relevant info for every texture
    keys = {}
    for bunch in [i for i in connected_components(image_graph) if len(i) > 1]:
        for node in bunch:
            keys[node] = node.name, raster_dict[node]

    # Iterate through each file that is part of the key
    for key, (template_name, default_image) in keys.items():

        # Load corresponding cluster map
        with open(template_directory + "\\" + os.path.split(template_name)[1] + ".json", 'r') as config:
            layer_map = json.load(config)['cluster_map']
        # Use corresponding cluster map
        image_clusters = filter.layer_decomposite(default_image, layer_map)
        templ_clusters = filter.layer_decomposite(raster_dict[template_name], layer_map)

        # Analyze each cluster
        segment_metalist = []
        for segment, template_segment in image_clusters, templ_clusters:
            segment_metalist.append(analyze_image(segment, template_segment, sections))

        meta_dict = {
            'group_name': template_name,
            'segment_dicts': json.dumps(segment_metalist)
        }

        output_path = os.path.split(output_directory + key)[0]

        # Create folder structure
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Save json file
        with open(output_path + "\\" + os.path.split(key)[1] + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file)


def analyze_image(image, template=None, granularity=10):

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

    data = {
        'hues': hues,
        'sats': sats,
        'vals': vals,
        'lightness': lightness,
        'variance': data_variance}

    # Equivalence flag
    equivalent = False
    if template is not None:
        if np.array_equal(image.get_opaque(), template.get_opaque()):
            equivalent = True
    data['equivalent'] = equivalent

    return data
