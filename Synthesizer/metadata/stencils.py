import json
import os

from Raster.Raster import Raster
from Raster import filters, analyze, math_utilities
import numpy as np


def make_stencil(stencil_name, quantity, stencil_staging, stencil_configs, colorize, relative_path):

    masks = []

    for id in range(quantity):
        stencil_path = os.path.normpath(stencil_staging + "\\" + stencil_name + "_" + str(id+1) + ".png")
        stencil = Raster.from_path(stencil_path, 'RGBA')
        masks.append(stencil.mask.tolist())

    stencil_path = stencil_staging + "\\" + stencil_name + "_1.png"
    stencil_data = dict(name=stencil_name,
                        shape=Raster.from_path(stencil_path, 'RGBA').shape.tolist(),
                        mask=masks,
                        colorize=colorize,
                        path=relative_path)

    with open(stencil_configs + '//' + stencil_name + ".json", 'w') as output_file:
        json.dump(stencil_data, output_file, sort_keys=True)


def apply_stencil(data, paths, resourcepack):
    mapping_path, json_data = data

    image_components = []
    for cluster_data in json_data['segment_dicts']:
        segment = Raster.from_path(
            paths.resource_skeletons + '//' + resourcepack + '//'
            + json_data['group_name'] + '_' + str(cluster_data['id']+1) + '.png', "RGBA")

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
        # print(lightness_adjustment)
        while(analyze.mean(staged_image, 'V') - abs(lightness_adjustment)
              < cluster_data['lightness']
              < analyze.mean(staged_image, 'V') + abs(lightness_adjustment)):

            # print(template_path + '\n'
            #       + str(cluster_data['lightness']) + ' ' + str(analyze.mean(staged_image, 'V')) + '\n'
            #       + str(lightness_adjustment))

            staged_image = filters.brightness(staged_image, lightness_adjustment)

        image_components.append(staged_image)

    output_image = filters.composite(image_components)

    # Output/save image
    full_path_output = str(mapping_path)\
        .replace(paths.mappings_metadata_custom, paths.output_path + '//' + resourcepack + '//')\
        .replace('.json', '')
    print('Generated: ' + mapping_path.replace(paths.mappings_metadata_custom, resourcepack + '\\').replace('.json', ''))

    if not os.path.exists(os.path.split(full_path_output)[0]):
        os.makedirs(os.path.split(full_path_output)[0])

    output_image.save(full_path_output)