import os
import json
import time
import ast
import colorsys
from multiprocessing import Process, Queue, cpu_count

from networkx.algorithms.components.connected import connected_components
import numpy as np

from scipy.spatial.distance import euclidean

from Raster.Raster import Raster
from Raster import math_utilities, analyze
from Raster import filter as filter_raster
from Synthesizer.Metadata.network import connectivity_sort


def template_metadata(template_directory, source_directory, image_graph):
    """Generate spectral cluster maps for the templates"""

    template_queue = Queue()

    pool = [Process(target=template_process,
            args=(template_queue, template_directory, source_directory), name=str(proc))
            for proc in range(cpu_count())]

    for proc in pool:
        proc.start()

    for bunch in connected_components(image_graph):
        bunch = connectivity_sort(bunch, image_graph)[0]
        first_image = Raster.from_path(source_directory + bunch, 'RGBA')

        if first_image.shape != (16, 16):
            # TODO: Perfect place to tie in GUI generator
            continue

        try:
            template_queue.put(source_directory + image_graph.node[bunch]['group_name'])
        except KeyError:
            continue

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
            Raster.from_path(source_directory + node, 'RGBA')
            keys[node] = image_graph.node[node]['group_name'], Raster.from_path(source_directory + node, 'RGBA')

    # Iterate through each file that is part of the key
    for key, (template_name, default_image) in keys.items():

        # Load corresponding cluster map
        try:
            with open(template_directory + "\\" + os.path.split(template_name)[1] + ".json", 'r') as config:
                layer_map = ast.literal_eval(json.load(config)['cluster_map'])
        except FileNotFoundError:
            print("Could not find: " + template_directory + "\\" + os.path.split(template_name)[1] + ".json")
            continue

        # Use corresponding cluster map to break image into pieces
        try:
            image_clusters = filter_raster.layer_decomposite(default_image, layer_map)
        except ValueError:
            continue
        templ_clusters = filter_raster.layer_decomposite(
            Raster.from_path(source_directory + template_name, 'RGBA'), layer_map)

        # Analyze each cluster
        segment_metalist = []
        for ident, (segment, template_segment) in enumerate(zip(image_clusters, templ_clusters)):
            segment_data = analyze_image(segment, template_segment, sections)
            segment_data['id'] = ident
            segment_metalist.append(segment_data)

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


def image_cluster(template_image):
    template_image.to_hsv()

    # Intuition on how many sections to split an image into
    sections = int(max(analyze.variance(template_image)) * 50)

    if sections < 2:
        layer_map = np.zeros(np.product(template_image.shape)).astype(np.int16)
    else:
        # Clustering algorithm
        layer_map = analyze.cluster(template_image, sections)

    layer_map = np.array(layer_map).astype(int)

    image_clusters = filter_raster.layer_decomposite(template_image, layer_map)

    return filter_raster.merge_similar(image_clusters, layer_map=layer_map)


def template_process(template_queue, template_directory, home):
    while True:
        time.sleep(1)
        template_name = template_queue.get()

        template_image = Raster.from_path(template_name, 'RGBA')
        image_clusters, guide = image_cluster(template_image)
        sections = len(image_clusters)

        print('-S: ' + str(len(image_clusters)) + ' | ' + template_name)

        # for index, cluster in enumerate(image_clusters):
        #     cluster.get_image().save(r"C:\Users\mike_000\Desktop\output\\" + cluster.name + str(index) + '.png')

        # Analyze each cluster, save to list of dicts
        segment_metalist = []
        for ident, segment in enumerate(image_clusters):
            cluster_data = analyze_image(segment, granularity=sections)
            cluster_data['id'] = ident
            segment_metalist.append(cluster_data)

        meta_dict = {
            'group_name': template_name.replace(home, ''),
            'segment_dicts': segment_metalist,
            'cluster_map': json.dumps(guide.tolist()),
            'shape': str(template_image.shape)
        }

        # Create folder structure
        if not os.path.exists(template_directory):
            os.makedirs(template_directory)

        # Save json file
        with open(template_directory + "\\" + os.path.split(template_name)[1] + ".json", 'w') as output_file:
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


def resource_cluster_correspondence(template_filename, resource_pack_path, file_metadata_path, template_metadata_path):

    group_name = json.loads(open(file_metadata_path + '\\' + template_filename + '.json', 'r').read())['group_name']
    template_metadata_json = json.loads(
        open(template_metadata_path + '\\' + os.path.split(group_name)[1] + '.json', 'r').read())

    template_name = resource_pack_path + '\\' + os.path.join(*(template_filename.split(os.path.sep)[1:]))
    template_image = Raster.from_path(template_name, 'RGBA')
    print(template_image.name)

    width_squared = (template_image.shape[0], template_image.shape[0])
    default_shape = ast.literal_eval(template_metadata_json['shape'])

    try:
        template_image = filter_raster.crop(template_image, (0, 0), width_squared)
    except ValueError:
        pass

    resource_clusters, resource_guide = image_cluster(template_image)
    resource_guide = np.reshape(resource_guide, width_squared)

    resource_guide_resized = []
    for coord_x in np.linspace(0, template_image.shape[0] - 1, default_shape[0]).astype(int):
        for coord_y in np.linspace(0, template_image.shape[1] - 1, default_shape[1]).astype(int):
            resource_guide_resized.append(resource_guide[coord_x, coord_y])

    # Resize to match default shape
    resource_guide = np.array(resource_guide_resized)
    default_guide = np.array(ast.literal_eval(template_metadata_json['cluster_map'])).reshape(default_shape)

    segment_metalist = []
    for ident, segment in enumerate(resource_clusters):
        segment_data = analyze_image(segment, granularity=len(resource_clusters))
        segment_data['id'] = ident
        segment_metalist.append(segment_data)

    default_segment_metalist = template_metadata_json['segment_dicts']

    resource_guide_binary = []
    for ident in range(max(resource_guide.flatten()) + 1):
        resource_guide_binary.append(np.equal(resource_guide, ident))

    default_guide_binary = []
    for ident in range(max(default_guide.flatten()) + 1):
        default_guide_binary.append(np.equal(default_guide, ident))

    shape = list(ast.literal_eval(template_metadata_json['shape']))
    # print(str(len(resource_guide_binary)) + str(len(default_guide_binary)))
    # print(str(len(segment_metalist)) + str(len(default_segment_metalist)))

    flow_matrix = np.zeros((len(resource_guide_binary), len(default_guide_binary)))
    for coord_x, guide_res in enumerate(resource_guide_binary):
        for coord_y, guide_def in enumerate(default_guide_binary):
            if match(segment_metalist[coord_x], default_segment_metalist[coord_y], guide_res, guide_def, shape):
                flow_matrix[coord_x, coord_y] = True

    return flow_matrix.astype(int), resource_guide


def match(data_a, data_b, guide_a, guide_b, shape):
    if abs(math_utilities.circular_mean(data_a['hues']) - math_utilities.circular_mean(data_b['hues'])) > .2:
        return False
    if abs(math_utilities.linear_mean(data_a['sats']) - math_utilities.linear_mean(data_b['sats'])) > .5:
        return False
    if abs(data_a['lightness'] - data_b['lightness']) > .5:
        return False

    # Clusters must be near each other
    points_a = []
    for coord_x, column in enumerate(guide_a.reshape(shape)):
        for coord_y, value in enumerate(column):
            if value:
                points_a.append((coord_x, coord_y))

    points_b = []
    for coord_x, column in enumerate(guide_b.reshape(shape)):
        for coord_y, value in enumerate(column):
            if value:
                points_b.append((coord_x, coord_y))

    try:
        mean_point_a = (np.average(np.array(points_a)[:, 0]), np.average(np.array(points_a)[:, 1]))
        mean_point_b = (np.average(np.array(points_b)[:, 0]), np.average(np.array(points_b)[:, 1]))
    except IndexError:
        print("Indice overflow")
        return False
    print(str(mean_point_a))
    print(str(mean_point_b))

    # Calculate euclidean distance
    proximity = euclidean(mean_point_a, mean_point_b)
    allowance = np.sqrt(np.prod(shape) * np.average((np.var(points_a), np.var(points_b)))) / 7

    print('Proximity: ' + str(proximity))
    print('Allowance: ' + str(allowance))

    if proximity > allowance:
        return False

    print('Match')
    return True



def binding_process(template_path, resource_pack, file_metadata, template_metadata, bindings_metadata):


def create_binding():
    resource_binding = {}
    try:
        flow_matrix, resource_guide = resource_cluster_correspondence(
            resource_template, resource_pack, file_metadata, template_metadata)
        resource_binding['cluster_map'] = str(resource_guide)
        resource_binding['flow_matrix'] = flow_matrix.tolist()
        resource_binding['relative_path'] = resource_template

        path_binding = self.bindings_metadata + '\\' + os.path.split(resource_template)[1] + '.json'

        with open(path_binding, 'w') as json_binding:
            json.dump(resource_binding, json_binding, sort_keys=True, indent=2)

    except FileNotFoundError:
        continue