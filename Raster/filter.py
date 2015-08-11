import copy
from math import pi, sin, cos, sqrt
from itertools import combinations

import numpy as np
import networkx
from networkx.algorithms.components.connected import connected_components

from Raster.analyze import mean, extrema
from Raster import Raster
from Raster.math_utilities import circular_mean, linear_mean, clamp


def colorize(raster, hue, sat=0., val=0., hue_opacity=1., sat_opacity=0, val_opacity=0):

    raster.to_hsv()

    # Modify each pixel
    for index, (h, s, v) in enumerate(raster.colors):

        # Blend in values at given opacity
        h = circular_mean([hue, h], [hue_opacity, 1 - hue_opacity])
        s = linear_mean([sat, s], [sat_opacity, 1 - sat_opacity])
        v = linear_mean([val, v], [val_opacity, 1 - val_opacity])

        raster.colors[index] = [h, s, v]

    return raster


def contrast(raster, value_multiplier):

    raster.to_hsv()

    avg_val = mean(raster, 'V')

    # period_hue = 1
    period_val = pi / min([avg_val, 1 - avg_val])

    min_val = min(raster.channel('V'))

    # Modify each pixel
    for index, (h, s, v) in enumerate(raster.colors):

        # Blend in values at given opacity
        v -= sin(period_val * (v - min_val)) * value_multiplier
        v = clamp(v, 0, 1)

        raster.colors[index] = [h, s, v]

    return raster


def brightness(raster, light_difference):
    raster.colors[:, 2] += light_difference
    minimum, maximum = extrema(raster, 'V')
    if minimum < 0:
        raster.colors[:, 2] -= minimum
    if maximum > 1:
        raster.colors[:, 2] -= (maximum - 1)

    raster.colors = np.clip(raster.colors, 0., 1.)
    return raster


def value_decomposite(raster, layers):
    """Slice image by a given number of lightness zones"""

    minimum, maximum = extrema(raster, 'V')
    # print("Minimum: " + str(minimum))
    # print("Maximum: " + str(maximum))

    brightnesses = raster.channel('V')

    raster_components = []
    layer_range = (maximum - minimum) / layers
    period = pi / layer_range
    # print("Layer Range: " + str(layer_range))
    # print("Period: " + str(period))

    for layer in range(layers):
        new_image = copy.deepcopy(raster)

        # Starting offset + layer spacings + half spacing
        horizontal_translation = minimum + layer_range * layer + layer_range / 2

        for index, lightness in enumerate(brightnesses):
            # If lightness is within mask's first period...
            if horizontal_translation - layer_range <= lightness <= horizontal_translation + layer_range:
                # Resolve edge case to preserve transparency in low and high lightness
                if minimum + layer_range / 2 <= lightness <= maximum - layer_range * .5:
                    bright_mask = cos(period * (lightness - horizontal_translation)) * .5 + .5
                else:
                    bright_mask = 1
            else:
                bright_mask = 0
            new_image.mask[index] = clamp(new_image.mask[index] * bright_mask)

        # print("Horizontal Translation: " + str(horizontal_translation))
        raster_components.append(new_image)

    return raster_components


def layer_decomposite(raster, layer_map):
    clustered_images = []
    for cluster in range(max(layer_map) + 1):
        filtered_mask = np.equal(cluster, layer_map) * raster.mask
        if sum(filtered_mask) > 0:
            new_image = copy.deepcopy(raster)
            new_image.mask = filtered_mask
            clustered_images.append(new_image)

    return clustered_images


def merge_similar(raster_list, layer_map=None):
    # If cluster layer_map is given, a modified layer_map reflecting merge changes will be returned.

    # Calculate average channel values for each cluster, producing a list of points
    coordinates = []
    for index, piece in enumerate(raster_list):
        coordinates.append((np.average(piece.get_opaque(), axis=0), index))

    # Calculates distance between two points
    def euclidean_distance(point_1, point_2=(0, 0, 0)):
        difference = point_2 - point_1

        # NOTE: Shitty tweak to separate hues weight
        difference[0] *= 1 + point_1[1]

        return sqrt(np.dot(difference, difference))

    image_whole = composite(raster_list)

    # Graph all pixels in 3D, fit a box to the data, then take the distance from the two furthest corners
    # Used to represent the magnitude, or scale of data.
    magnitude = euclidean_distance(np.amin(image_whole.get_opaque(), axis=0), np.amax(image_whole.get_opaque(), axis=0))
    # print(magnitude / len(clustered_images))

    # Calculate difference between each cluster.
    # If said distance is beneath a threshold, flag the pair for merging
    combine_list = []
    for pair in combinations(coordinates, 2):
        cluster_differentiation = euclidean_distance(pair[0][0], pair[1][0])

        if cluster_differentiation < magnitude * 1.5 / len(raster_list):
            combine_list.append((pair[0][1], pair[1][1]))

    # Combine all pairs with shared elements using network graphs
    def to_graph(node_collection):
        model = networkx.Graph()
        for nodes in node_collection:
            model.add_nodes_from(nodes)
            model.add_edges_from(get_edges(nodes))
        return model

    def get_edges(nodes):
        nodes_iterator = iter(nodes)
        last = next(nodes_iterator)

        for current in nodes_iterator:
            yield last, current
            last = current

    # Conserves clusters with no relations
    for index in range(len(raster_list)):
        combine_list.append([index])

    composition_graph = to_graph(combine_list)

    # Actual image compositing to group similar clusters
    clustered_combined_images = []
    image_bunches = list(connected_components(composition_graph))

    for indice_set in image_bunches:
        clustered_combined_images.append(composite(np.array(raster_list)[indice_set]))

    if layer_map is not None:
        layer_map_blank = np.zeros((np.product(raster_list[0].shape))).astype(np.int16)

        for index, image in enumerate(clustered_combined_images):
            layer_map_blank[np.where(image.mask > 0.)] = index

        return clustered_combined_images, layer_map_blank

    return clustered_combined_images


def composite(raster_list):
    """Combine all input layers with additive alpha blending"""

    pixel_layers = []
    for img in raster_list:
        pixel_layers.append(img.with_alpha())

    pixel_accumulator = []
    mask_construct = []

    # Take transpose of pixel layers to produce a list of corresponding pixels
    for pixel_profile in np.array(list(zip(*pixel_layers))):

        # Opacity is the sum of alpha channels
        opacity = sum(pixel_profile[:, 3])

        # If one of the pixels has opacity
        if opacity != 0:
            pixel = []

            # Treat opacity as weight
            weights = pixel_profile[:, 3]

            # Condense profile down into one representative pixel
            for channel_index, channel_id in enumerate(raster_list[0].mode):
                if channel_id == 'H':
                    pixel.append(circular_mean(pixel_profile[:, channel_index], weights))
                else:
                    pixel.append(linear_mean(pixel_profile[:, channel_index], weights))
            mask_construct.append(float(clamp(opacity)))

            pixel_accumulator.append(pixel)

        else:
            pixel_accumulator.append([0., 0., 0.])
            mask_construct.append(0.)

    return Raster.Raster(
        pixel_accumulator, raster_list[0].shape, raster_list[0].mode, mask_construct, name=raster_list[0].name)


def resize(raster, size):
    # No interpolation

    pixels = np.zeros((size[0], size[1], raster.colors.shape[1]))
    mask = np.zeros(size)

    tiered = raster.get_tiered()

    for x_source, x_target in enumerate(np.linspace(0, raster.shape[0]-1, size[0])):
        for y_source, y_target in enumerate(np.linspace(0, raster.shape[1]-1, size[1])):
            pixel = tiered[int(x_target), int(y_target)]
            pixels[x_source, y_source] = pixel[0:3]
            mask[x_source, y_source] = pixel[3]

    return Raster.Raster(pixels.reshape((np.product(size), raster.colors.shape[1])),
                         np.array(size),
                         raster.mode,
                         mask.reshape(np.product(size)),
                         name=raster.name)
