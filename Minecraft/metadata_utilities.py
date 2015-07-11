import os
import json
import colorsys

import networkx
from networkx.algorithms.components.connected import connected_components, connected_component_subgraphs
from networkx.readwrite import json_graph

from itertools import combinations, chain
from collections import defaultdict

from Raster.Raster import Raster
from Raster import filter, math_utilities, analyze

import numpy as np
from multiprocessing import Process, Queue, cpu_count, Lock, Manager
from multiprocessing.managers import BaseManager, DictProxy
import time

import ast

class DictManager(BaseManager):
    pass

DictManager.register('defaultdict', defaultdict, DictProxy)


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


def indexing_process(path_queue, raster_lock, raster_dict, target):

    def threshold(array_in, threshold=0.5):
        array_mask = array_in.copy()
        array_mask[array_mask > threshold] = 1.0
        array_mask[array_mask <= threshold] = 0.0

        return array_mask

    while True:
        full_path = path_queue.get()
        try:
            print(full_path)
            candidate = Raster.from_path(full_path, 'RGBA')
            image_hash = np.array_str(threshold(candidate.mask))

            # Categorize images by thresholded layer mask
            with raster_lock:
                raster_dict[image_hash].append(full_path.replace(target, ""))

        except OSError:
            continue


def image_hash(target, init=None):

    raster_dict_lock = Lock()
    manager = DictManager()
    manager.start()
    raster_dict = manager.defaultdict(list)

    if init is not None:
        raster_dict = init

    flat_listing = chain(*raster_dict.values())
    file_queue = Queue()

    pool = [Process(target=indexing_process, args=(file_queue, raster_dict_lock, raster_dict, target), name=str(proc))
        for proc in range(cpu_count())]

    for proc in pool:
        proc.start()

    for root, folders, files in os.walk(target):
        for current_file in files:
            full_path = root + "\\" + current_file

            if full_path.endswith('.png') and full_path not in flat_listing:
                file_queue.put(full_path)

    while not file_queue.empty():
        time.sleep(1)

    for proc in pool:
        proc.terminate()

    return dict(raster_dict)


def load_paths(root, paths):
    raster_dict = {}

    for path in paths:
        if path.endswith('.png'):
            try:
                candidate = Raster.from_path(path, 'RGBA')

                # Categorize images by thresholded layer mask
                raster_dict[path.replace(root, "")] = candidate

            except OSError:
                continue

    return raster_dict


def network_prune(network, raster_dict):
    raster_dict_flat = {}
    for image_grouping in raster_dict.values():
        raster_dict_flat.update(image_grouping)

    for node in network.nodes():
        if node not in raster_dict_flat.keys():
            network.remove_node(node)
    return network


def connectivity_sort(network, threshold=1):
    """Returns each bunch sub-ordered by connectivity"""

    connectivity_net = []

    def node_strength(node):
        node_edges = network.edges(node, data=True)
        if node_edges:
            weight_total = 0
            for weight_dict in np.array(node_edges)[..., 2]:
                weight_total += weight_dict['weight']
            return weight_total
        return 0

    for bunch in connected_components(network):
        connectivity_net.append(sorted(bunch, key=node_strength))

    return [i for i in connectivity_net if len(i) > threshold]


def network_images(raster_dict, threshold=0, network=None):

    if network is None:
        network = networkx.Graph()

    new_elements = set(raster_dict.keys()) - set(network.nodes())
    network.add_nodes_from(new_elements)

    for group_outer, group_inner in combinations(connectivity_sort(network), 2):
        correlation = analyze.correlate(
            raster_dict[group_outer[0]], raster_dict[group_inner[0]])

        if correlation > threshold:
            # print("Matched: " + str(node_outer[0]) + ' & ' + str(node_inner[0]))
            network.add_edge(group_inner[0], group_outer[0], weight=correlation)

    # Name each bunch
    for bunch in [i for i in connected_component_subgraphs(network) if len(i) > 1]:
        max_node_strength = 0

        # Name bunch from greatest node
        greatest_node = None
        name = None
        for node in bunch:

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


def template_metadata(template_directory, source_directory, image_graph):
    """Generate spectral cluster maps for the templates"""

    template_queue = Queue()

    pool = [Process(target=template_process, args=(template_queue, template_directory), name=str(proc))
            for proc in range(cpu_count())]

    for proc in pool:
        proc.start()

    for bunch in [i for i in connected_components(image_graph) if len(i) > 1]:
        first_image = Raster.from_path(source_directory + bunch[0])
        if first_image.shape != (16, 16):
            # TODO: Perfect place to tie in GUI generator
            continue

        template_queue.put(source_directory + image_graph.node[bunch[0]]['group_name'])

    while not template_queue.empty():
        time.sleep(1)

    for proc in pool:
        proc.terminate()


def file_metadata(output_directory, template_directory, source_directory, image_graph, sections=3):
    """Save representative data to json files in meta pack"""
    if not os.path.exists(template_directory):
        os.makedirs(template_directory)

    template_data = {}
    for json_filename in os.listdir(template_directory):
        with open(template_directory + json_filename, 'r') as json_file:
            json_data = json.load(json_file)
            template_data[json_data['group_name']] = json_data

    # Retrieve the relevant info for every texture
    keys = {}
    for bunch in [i for i in connected_components(image_graph) if len(i) > 1]:
        for node in bunch:
            Raster.from_path(source_directory + node)
            keys[node] = image_graph.node[node]['group_name'], raster_dict[node]

    # Iterate through each file that is part of the key
    for key, (template_name, default_image) in keys.items():

        # Load corresponding cluster map
        try:
            with open(template_directory + "\\" + os.path.split(template_name)[1] + ".json", 'r') as config:
                layer_map = ast.literal_eval(json.load(config)['cluster_map'])
        except FileNotFoundError:
            print("Could not find: " + template_directory + "\\" + os.path.split(template_name)[1] + ".json")
            continue

        # Use corresponding cluster map
        image_clusters = filter.layer_decomposite(default_image, layer_map)
        templ_clusters = filter.layer_decomposite(raster_dict[template_name], layer_map)

        # Analyze each cluster
        segment_metalist = []
        for segment, template_segment in zip(image_clusters, templ_clusters):
            segment_metalist.append(analyze_image(segment, template_segment, sections))

        meta_dict = {
            'group_name': template_name,
            'segment_dicts': segment_metalist
        }

        output_path = os.path.split(output_directory + key)[0]

        # Create folder structure
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Save json file
        with open(output_path + "\\" + os.path.split(key)[1] + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file, sort_keys=True, indent=2)


def template_process(template_queue, template_directory):
    while True:
        template_image = template_queue.get()

        template_name = template_image.name
        template_image.to_hsv()

        # Intuition on how many sections to split an image into
        sections = int(max(analyze.variance(template_image)) * 50)

        if sections < 2:
            layer_map = np.zeros(np.product(template_image.shape)).astype(np.int16)
            sections = 1
        else:
            # Clustering algorithm
            layer_map = analyze.cluster(template_image, sections)

        image_clusters = filter.layer_decomposite(template_image, layer_map)
        image_clusters, guide = filter.merge_similar(image_clusters, layer_map=layer_map)

        print('-S: ' + str(len(image_clusters)) + ' | ' + template_name)

        # for index, cluster in enumerate(image_clusters):
        #     cluster.get_image().save(r"C:\Users\mike_000\Desktop\output\\" + cluster.name + str(index) + '.png')

        # Analyze each cluster, save to list of dicts
        segment_metalist = []
        for segment in image_clusters:
            segment_metalist.append(analyze_image(segment, granularity=sections))

        meta_dict = {
            'group_name': template_name,
            'segment_dicts': segment_metalist,
            'cluster_map': json.dumps(guide.tolist())
        }

        # Create folder structure
        if not os.path.exists(template_directory):
            os.makedirs(template_directory)

        # Save json file
        with open(template_directory + "\\" + template_image.name + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file, sort_keys=True, indent=2)


def analyze_image(image, template=None, granularity=10):
    colors = analyze.color_extract(image, granularity)

    hues = []
    sats = []
    vals = []

    for color in colors:
        r, g, b, a = color
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hues.append(h)
        sats.append(s)
        vals.append(v)

    hues = math_utilities.circular_sort(list(set(hues)))
    sats = sorted(list(set(sats)))[::-1]
    vals = sorted(list(set(vals)))

    data_variance = analyze.variance(image, 'V')
    lightness = analyze.mean(image, 'V')

    data = {
        'hues': hues,
        'sats': sats,
        'vals': vals,
        'lightness': lightness,
        'variance': data_variance}

    # Equivalence flag
    if template is not None:
        equivalent = False

        image.to_rgb()
        template.to_rgb()

        print('\nImage: ' + image.name +
              '\nTemplate: ' + template.name +
              '\nDifference: ' + str(np.sum(image.colors - template.colors)))
        if round(np.sum(image.colors - template.colors), 2) == 0.:
            equivalent = True
        data['equivalent'] = equivalent

    return data
