import os
import json
import colorsys

import networkx
from networkx.algorithms.components.connected import connected_components, connected_component_subgraphs
from networkx.readwrite import json_graph

from itertools import combinations
import operator

from Raster.Raster import Raster
from Raster import filter, math_utilities, analyze

import numpy as np
from multiprocessing import Process, Queue, cpu_count

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

            if full_path.endswith('.png'):
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

            # Quick return in case template already defined
            if 'group_name' in network.node[point]:
                return point

            bunch_build[point] = network.degree(point)
        return max(bunch_build.items(), key=operator.itemgetter(1))[0]

    for group_outer, group_inner in combinations(connected_components(network), 2):
        correlation = analyze.correlate(raster_dict[center(group_outer)], raster_dict[center(group_inner)])

        if correlation > threshold:
            # print("Matched: " + str(node_outer[0]) + ' & ' + str(node_inner[0]))
            network.add_edge(center(group_inner), center(group_outer), weight=correlation)

    # Name each bunch
    for bunch in [i for i in connected_component_subgraphs(network) if len(i) > 1]:
        max_node_strength = 0

        # Name bunch from greatest node
        greatest_node = None
        name = None
        for node in bunch:

            node_strength = 0
            for edge in list(bunch.edge[node].values()):
                node_strength += edge['weight']

            if node_strength > max_node_strength:
                max_node_strength = node_strength
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


def template_metadata(template_directory, image_graph, raster_dict):
    """Generate spectral cluster maps for the templates"""

    template_queue = Queue()

    pool = [Process(target=template_process, args=(template_queue, template_directory)) for proc in range(cpu_count())]
    for proc in pool:
        proc.start()

    for bunch in [i for i in connected_components(image_graph) if len(i) > 1]:
        if raster_dict[bunch[0]].shape != (16, 16):
            # TODO: Perfect place to tie in GUI generator
            continue

        template_queue.put(raster_dict[image_graph.node[bunch[0]]['group_name']])
    for proc in pool:
        proc.join()

def file_metadata(output_directory, template_directory, image_graph, raster_dict, sections=3):
    """Save representative data to json files in meta pack"""

    template_data = {}
    for json_filename in os.listdir(template_directory + '\\meta\\'):
        with open(template_directory + '\\meta\\' + json_filename, 'r') as json_file:
            json_data = json.load(json_file)
            template_data[json_data['group_name']] = json_data

    # Retrieve the relevant info for every texture
    keys = {}
    for bunch in [i for i in connected_components(image_graph) if len(i) > 1]:
        for node in bunch:
            keys[node] = image_graph.node[node]['group_name'], raster_dict[node]

    # Iterate through each file that is part of the key
    for key, (template_name, default_image) in keys.items():

        # Load corresponding cluster map
        with open(template_directory + "\\meta\\" + os.path.split(template_name)[1] + ".json", 'r') as config:
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
            json.dump(meta_dict, output_file, sort_keys=True, indent=2)

def template_process(template_queue, template_directory):
    while True:
        template_image = template_queue.get()

        template_name = template_image.name
        template_image.to_rgb()
        sections = int(max(analyze.variance(template_image)) * 15)
        print(template_name)
        print(analyze.variance(template_image))
        print("Sections: " + str(sections))

        layer_map = []
        if sections < 2:
            layer_map = np.zeros(np.product(template_image.shape)).astype(np.int16)
            sections = 1
        else:
            # Clustering algorithm
            layer_map = analyze.cluster(template_image, sections)

        image_clusters = filter.layer_decomposite(template_image, layer_map)


        image_clusters, guide = filter.merge_similar(image_clusters, layer_map=layer_map)
        print(len(image_clusters))
        print(guide)
        for index, cluster in enumerate(image_clusters):
            cluster.get_image().save(r"C:\Users\mike_000\Desktop\output\\" + cluster.name + str(index) + '.png')

        # Analyze each cluster, save to list of dicts
        segment_metalist = []
        for segment in image_clusters:
            print(type(segment))
            segment_metalist.append(analyze_image(segment, granularity=sections))

        meta_dict = {
            'group_name': template_name,
            'segment_dicts': segment_metalist,
            'cluster_map': str(list(guide))
        }

        # Create folder structure
        if not os.path.exists(template_directory):
            os.makedirs(template_directory)

        # Save json file
        with open(template_directory + "\\" + template_image.name + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file, sort_keys=True, indent=2)

def analyze_image(image, template=None, granularity=10):
    colors = analyze.color_extract(image, granularity)

    print(colors)

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
    equivalent = False
    if template is not None:
        if np.array_equal(image.get_opaque(), template.get_opaque()):
            equivalent = True
    data['equivalent'] = equivalent

    return data
