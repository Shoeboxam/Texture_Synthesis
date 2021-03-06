import os
import json
import ast

import numpy as np
from scipy.spatial.distance import euclidean

from Raster.Raster import Raster
from Raster import filters
from Utilities import math
from Synthesizer.images import analyze_image
from Synthesizer.cluster import spectral_cluster
from Utilities.vectorize import vectorize


def build(paths, template_paths):
    """Generate all bindings"""
    if not os.path.exists(paths.bindings_metadata):
        os.mkdir(paths.bindings_metadata)
    vectorize(template_paths, make_binding, [paths])


def make_binding(resource_template, paths):
    """Bind a single template"""
    resource_binding = {}
    try:
        flow_matrix, resource_guide = resource_cluster_correspondence(paths, resource_template)

        resource_binding['cluster_map'] = ','.join(map(str, resource_guide.flatten().astype(np.int8).tolist()))
        resource_binding['flow_matrix'] = flow_matrix.tolist()
        resource_binding['relative_path'] = resource_template

        path_binding = paths.bindings_metadata + '\\' + os.path.split(resource_template)[1] + '.json'

        with open(path_binding, 'w') as json_binding:
            json.dump(resource_binding, json_binding, sort_keys=True, indent=2)

    except FileNotFoundError:
        pass


def resource_cluster_correspondence(paths, template_filename):

    # Load relevant images and json files
    full_template_path = paths.mappings_metadata + '\\' + template_filename + '.json'
    group_name = json.loads(open(full_template_path, 'r').read())['group_name']
    template_metadata_json = json.loads(
        open(paths.template_metadata + '\\' + os.path.split(group_name)[1] + '.json', 'r').read())
    template_name = paths.resource_pack + '\\' + os.path.join(*(template_filename.split(os.path.sep)[1:]))
    template_image = Raster.from_path(template_name, 'RGBA')

    print(template_image.name)
    width_squared = (template_image.shape[0], template_image.shape[0])
    default_shape = ast.literal_eval(template_metadata_json['shape'])

    # TODO: Add support for animations here. Currently takes first frame only
    try:
        template_image = filters.crop(template_image, (0, 0), width_squared)
    except ValueError:
        pass

    # Break resource pack template image into chunks- expensive
    # TODO: Diff-based clustering
    resource_clusters, resource_guide = spectral_cluster(template_image)
    resource_guide = np.reshape(resource_guide, width_squared)

    # Resize resource pack template image's cluster guide to the size of the default pack template image's cluster guide
    resource_guide_resized = []
    for coord_x in np.array(np.linspace(0, template_image.shape[0] - 1, default_shape[0])).astype(int):
        for coord_y in np.array(np.linspace(0, template_image.shape[1] - 1, default_shape[1])).astype(int):
            resource_guide_resized.append(resource_guide[coord_x, coord_y])

    resource_guide_resized = np.array(resource_guide_resized)

    default_guide = np.array(ast.literal_eval(template_metadata_json['cluster_map'])).reshape(default_shape)

    # Analyze each cluster in resource pack template image and save to list of dictionaries
    segment_metalist = []
    for segment in resource_clusters:
        segment_metalist.append(analyze_image(segment, granularity=len(resource_clusters)))

    default_segment_metalist = template_metadata_json['segment_dicts']

    # Change format from [ 0 1 2 ] to [ 1 0 0 ], [ 0 1 0 ], [ 0 0 1 ]
    resource_guide_binary = []
    for ident in range(max(resource_guide_resized.flatten()) + 1):
        resource_guide_binary.append(np.equal(resource_guide_resized, ident))

    default_guide_binary = []
    for ident in range(max(default_guide.flatten()) + 1):
        default_guide_binary.append(np.equal(default_guide, ident))

    # Load dimensions from default metadata
    shape = list(ast.literal_eval(template_metadata_json['shape']))

    # Match each resource cluster to each default cluster
    flow_matrix = np.zeros((len(resource_guide_binary), len(default_guide_binary)))
    for coord_x, guide_res in enumerate(resource_guide_binary):
        for coord_y, guide_def in enumerate(default_guide_binary):
            if match(segment_metalist[coord_x], default_segment_metalist[coord_y], guide_res, guide_def, shape):
                flow_matrix[coord_x, coord_y] = True

    return flow_matrix.astype(int), resource_guide


def match(data_a, data_b, guide_a, guide_b, shape):
    """Determine if two data sets are sufficiently similar"""
    threshold = .7

    # Check hue, sat and lightness for similarity
    if abs(math.circular_mean(data_a['hues']) - math.circular_mean(data_b['hues'])) > threshold:
        return False
    if abs(math.linear_mean(data_a['sats']) - math.linear_mean(data_b['sats'])) > threshold:
        return False
    if abs(data_a['lightness'] - data_b['lightness']) > threshold:
        return False

    # Clusters must be near each other

    # Reformat binary listing into indexed array of points
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

    # Find center of cluster
    try:
        mean_point_a = (np.average(np.array(points_a)[:, 0]), np.average(np.array(points_a)[:, 1]))
        mean_point_b = (np.average(np.array(points_b)[:, 0]), np.average(np.array(points_b)[:, 1]))
    except IndexError:
        # print("Indice overflow")
        return False

    # Calculate euclidean distance between cluster centers
    proximity = euclidean(mean_point_a, mean_point_b)

    # Allow greater differences in proximity should the clusters have large spreads
    allowance = np.sqrt(np.prod(shape) * np.average((np.var(points_a), np.var(points_b)))) / 7

    # print('Proximity: ' + str(proximity) + '\n' +
    #       'Allowance: ' + str(allowance))

    if proximity > allowance:
        return False

    return True
