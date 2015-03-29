import numpy as np
from image_analysis import *
from color_utilities import *


def colorize(raster, hue, sat, val, hue_opacity=1., sat_opacity=.5, val_opacity=.5):

    raster.to_hsv()

    for index, (h, s, v) in enumerate(raster.colors):
        h = circular_mean([h, hue], [hue_opacity, 1 - hue_opacity])
        s = (sat * sat_opacity) + s * (1 - sat_opacity)
        v = (val * val_opacity) + v * (1 - val_opacity)
        raster.colors[index] = [h, s, v]

    return raster


def contrast(raster, hue, sat, val, hue_opacity=1., sat_opacity=.5, val_opacity=.5):

    raster.to_hsv()

    avg_hue = hue_mean(raster)
    avg_val = val_mean(raster)
    avg_sat = sat_mean(raster)

    for index, (h, s, v) in enumerate(raster.colors):
        # TODO: Deviate data
        pass
    return


def mask_alpha(raster, mask):
    for index, (alpha, transparency) in enumerate(zip(raster.mask, mask)):
        raster.mask[index] = [alpha * transparency]

    return raster

def image_decompose(raster, layers):
    """Slice image by a given number of lightness zones"""

    minimum, maximum = lightness_extrema(raster)

    raster_components = []
    for layer in range(layers):
        # CREATE MASK
        mask

        # APPLY MASK
        raster_components.append(mask_alpha(raster, mask))


def image_composite(raster_list):
    """Combine all input layers with additive alpha blending"""

    pixel_layers = []
    for raster in raster_list:
        pixel_layers.append(raster.pixels)

    pixel_accumulator = []

    # Take transpose of pixel layers to produce a list of corresponding pixels
    for pixel_profile in zip(*pixel_layers):

        # Opacity is the sum of alpha channels
        opacity = sum(pixel_profile[:, 3])

        # If one of the pixels has opacity
        if opacity != 0:
            pixel = []

            # Treat opacity as weight
            weights = pixel_profile[:, 3]

            # Condense profile down into one representative pixel
            pixel.append(circular_mean(pixel_profile[:, 0], weights))  # H
            pixel.append(linear_mean(pixel_profile[:, 1], weights))    # S
            pixel.append(linear_mean(pixel_profile[:, 2], weights))    # V
            pixel.append(opacity)                                      # A
            pixel_accumulator.append(pixel)
        else:
            pixel_accumulator.append([0, 0, 0, 0])

    return Raster.fromarray(pixel_accumulator, 'HSV')
