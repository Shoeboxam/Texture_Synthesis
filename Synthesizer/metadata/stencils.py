import json
import os
import math

from Raster.Raster import Raster
from Raster import filters, analyze


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

        if not cluster_data['colorize']:
            image_components.append(segment)
            continue

        # Adjust contrast
        contrast_mult = abs(analyze.variance(segment, 'V') - math.sqrt(cluster_data['variance'])) * .1
        segment = filters.contrast(segment, contrast_mult)
        # Adjust coloration
        layer_count = len(cluster_data['hues'])
        components = filters.value_decomposite(segment, layer_count)
        colorized_components = []
        for i, layer in enumerate(components):
            layer = filters.colorize(layer, cluster_data['hues'][i], cluster_data['sats'][i], 0, 1, 1, 0)
            colorized_components.append(layer)
        staged_image = filters.composite(colorized_components)

        # Adjust lightness
        lightness_adjustment = cluster_data['lightness'] - analyze.mean(segment, 'V')
        staged_image = filters.brightness(staged_image, lightness_adjustment)
        image_components.append(staged_image)

    for component in image_components:
        component.to_rgb()

    output_image = filters.composite(image_components)

    # Output/save image
    full_path_output = str(mapping_path)\
        .replace(paths.mappings_metadata_custom, paths.output_path + '//' + resourcepack + '//')\
        .replace('.json', '')
    print('Generated: ' + mapping_path.replace(paths.mappings_metadata_custom, resourcepack + '//').replace('.json', ''))

    if not os.path.exists(os.path.split(full_path_output)[0]):
        os.makedirs(os.path.split(full_path_output)[0])

    if os.path.exists(full_path_output):
        os.remove(full_path_output)
    output_image.save(full_path_output)
