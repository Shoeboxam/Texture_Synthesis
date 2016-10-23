import colorsys
import os
import json
import pathlib

import numpy as np

from Raster.Raster import Raster
from Raster import math_utilities, analyze, filters
from Utilities.vectorize import vectorize

np.set_printoptions(precision=2, linewidth=1000)


def populate_images(paths, binding_ids):

    template_paths = []
    for root, folders, files in os.walk(paths.mappings_metadata):
        for image_file in files:
            full_path = os.path.join(root, image_file)

            with open(full_path, 'r') as json_file:
                mapping_data = json.load(json_file)

            template_name = os.path.split(mapping_data['group_name'])[1]
            if template_name in binding_ids:

                binding_path = paths.bindings_metadata + os.path.split(binding_ids[template_name])[1] + '.json'
                try:
                    binding_data = json.load(open(binding_path, 'r'))
                except FileNotFoundError:
                    continue

                template_paths.append((full_path, mapping_data, binding_data))

    vectorize(template_paths, apply_template, [paths])


def apply_template(data, paths):
    mapping_path, json_data, binding_json_data = data
    template_path = paths.resource_pack + '\\'.join(pathlib.Path(binding_json_data['relative_path']).parts[1:])
    # Split into clusters
    layer_guide = np.array(list(map(int, binding_json_data['cluster_map'].split(','))))

    image = Raster.from_path(template_path, 'RGBA')
    pieces = filters.layer_decomposite(image, layer_guide)

    altered_pieces = []
    flow_matrix = np.array(binding_json_data['flow_matrix'])

    for ident, segment in enumerate(pieces):

        for resource_cluster_id, match_data in enumerate(flow_matrix[ident, :]):
            for default_cluster_id, match in enumerate(flow_matrix[:, resource_cluster_id]):

                cluster_data = json_data['segment_dicts'][resource_cluster_id]
                if match and not cluster_data['equivalent']:

                    # Adjust contrast
                    contrast_mult = abs(analyze.variance(segment, 'V') - cluster_data['variance']) * .1
                    staged_image = filters.contrast(segment, contrast_mult)

                    # Adjust coloration
                    layer_count = len(cluster_data['hues'])*2
                    components = filters.value_decomposite(staged_image, layer_count)

                    sat_poly_raw = math_utilities.polyfit(
                        np.linspace(0, 1, len(cluster_data['sats'])), cluster_data['sats'])

                    sorted_hues = math_utilities.circular_sort(cluster_data['hues'])
                    linear_mapped_hues = (np.array(sorted_hues) - sorted_hues[0]) % 1
                    hue_poly = math_utilities.polyfit(np.linspace(0, 1, len(cluster_data['hues'])), linear_mapped_hues)

                    colorized_components = []
                    for index, layer in enumerate(components):

                        normalized_index = float(index) / len(components)

                        hue_target = (math_utilities.polysolve(hue_poly, normalized_index) + sorted_hues[0]) % 1
                        sat_target = math_utilities.polysolve(sat_poly_raw, normalized_index)

                        # Reduce sat in lighter areas of image
                        mean_lightness = analyze.mean(layer, 'V')
                        sat_reduction = pow(mean_lightness, len(components)) * sat_target
                        sat_target -= sat_reduction
                        sat_target = math_utilities.clamp(sat_target)

                        layer = filters.colorize(layer, hue_target, sat_target, 0, 1., 1., 0.0)
                        colorized_components.append(layer)

                    staged_image = filters.composite(colorized_components)

                    # Adjust lightness
                    lightness_adjustment = cluster_data['lightness'] - analyze.mean(segment, 'V')
                    print(lightness_adjustment)
                    while(analyze.mean(staged_image, 'V') - abs(lightness_adjustment)
                          < cluster_data['lightness']
                          < analyze.mean(staged_image, 'V') + abs(lightness_adjustment)):

                        print(template_path + '\n'
                              + str(cluster_data['lightness']) + ' ' + str(analyze.mean(staged_image, 'V')) + '\n'
                              + str(lightness_adjustment))

                        staged_image = filters.brightness(staged_image, lightness_adjustment)

                else:
                    staged_image = segment
            altered_pieces.append(staged_image)

    output_image = filters.composite(altered_pieces)

    output_image.mask = image.mask

    # Output/save image
    full_path_output = str(mapping_path).replace(paths.mappings_metadata, paths.output_path).replace('.json', '')
    print(full_path_output)

    if not os.path.exists(os.path.split(full_path_output)[0]):
        os.makedirs(os.path.split(full_path_output)[0])

    output_image.get_image().save(full_path_output)


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


def load_paths(root, paths):
    raster_dict = {}

    for path in paths:
        if path.endswith('.png'):
            try:
                candidate = Raster.from_path(root + path, 'RGBA')

                # Categorize images by thresholded layer mask
                raster_dict[path.replace(root, "")] = candidate

            except OSError:
                continue

    return raster_dict