from itertools import combinations
import os
import json

import networkx
from networkx import connected_component_subgraphs
from networkx.readwrite import json_graph
import numpy as np

from Raster import analyze
from Raster.Raster import Raster
from Utilities.vectorize import vectorize


def load_graph(path):
    try:
        json_data = open(path, 'r')
        image_graph = json_graph.node_link_graph(eval(json_data.read()))
        json_data.close()
    except FileNotFoundError:
        image_graph = networkx.Graph()
    return image_graph


def save_graph(path, graph):
    with open(path, 'w+') as json_file:
        json_file.write(str(json_graph.node_link_data(graph)))


def alpha_categorize(paths):
    """Weakly group images to partition set size- crucial optimization step"""

    if os.path.exists(paths.home + '//metadata//preprocess.json'):
        clumped_paths = json.loads(open(paths.home + '//metadata//preprocess.json').read())
    else:
        file_listing = []

        for root, folders, files in os.walk(paths.default_patches):
            for current_file in files:
                full_path = root + "\\" + current_file

                if full_path.endswith('.png'):
                    file_listing.append(full_path)

        clumped_paths = vectorize(file_listing, image_hash, args=paths.default_patches, returns=True)

    with open(paths.home + '//metadata//preprocess.json', 'w') as json_file:
        json.dump(clumped_paths, json_file)


def image_hash(full_path, target, raster_lock, raster_dict):
    def threshold(array_in, thresh=0.5):
        array_mask = array_in.copy()
        array_mask[array_mask > thresh] = 1.0
        array_mask[array_mask <= thresh] = 0.0

        return array_mask

    try:
        image_path = full_path.replace(target, "")
        candidate = Raster.from_path(full_path, 'RGBA')
        image_hash_id = ''.join(char for char in np.array_str(threshold(candidate.mask)) if char.isdigit())

        # Categorize images by thresholded layer mask
        with raster_lock:
            listobj = raster_dict[image_hash_id]
            listobj.append(image_path)
            raster_dict[image_hash_id] = listobj

    except OSError:
        pass


def connectivity_sort(bunch, network):
    """Returns a given bunch ordered by connectivity"""

    def node_strength(node):
        node_edges = network.edges(node, data=True)
        if node_edges:
            weight_total = 0
            for weight_dict in np.array(node_edges)[..., 2]:
                weight_total += weight_dict['weight']
            return weight_total
        return 0
    return sorted(bunch, key=node_strength)


def network_images(raster_dict, threshold=0, network=None):
    """Given a group of images, create a graph of interconnections"""

    if network is None:
        network = networkx.Graph()
    new_elements = set(raster_dict.keys()) - set(network.nodes())
    network.add_nodes_from(new_elements)

    for group_outer, group_inner in combinations(connectivity_sort(list(new_elements), network), 2):
        correlation = analyze.correlate(
            raster_dict[group_outer], raster_dict[group_inner])
        if correlation > threshold:
            # print("Matched: " + str(node_outer[0]) + ' & ' + str(node_inner[0]))
            network.add_edge(group_inner, group_outer, weight=correlation)

    # Name each bunch
    for bunch in filter(lambda group: len(group) > 1, connected_component_subgraphs(network)):

        max_node_strength = 0

        # Name bunch from greatest node
        greatest_node = None
        name = None
        for node in bunch.nodes():

            strength = 0
            for edge in list(bunch.edge[node].values()):
                strength += edge['weight']

            if strength > max_node_strength:
                max_node_strength = strength
                greatest_node = node

            # Collect names while determining greatest node
            if 'group_name' in network.node[node]:
                name = network.node[node]['group_name']

        if name is None:
            name = greatest_node

        # Apply new name to all nodes in bunch
        for node in bunch:
            network.node[node]['group_name'] = name

    # for group in connected_components(network):
    #     if len(group) > 1:
    #         for node in group:
    #             print(node)
    #         print(" ")

    return network