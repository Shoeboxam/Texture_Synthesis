from image_analysis import *
from color_utilities import *
from math import cos
from math import sin


def colorize(raster, hue, sat, val, hue_opacity=1., sat_opacity=.5, val_opacity=.5):

    raster.to_hsv()

    # Modify each pixel
    for index, (h, s, v) in enumerate(raster.colors):

        # Blend in values at given opacity
        h = circular_mean([h, hue], [hue_opacity, 1 - hue_opacity])
        s = linear_mean([sat, s], [sat_opacity, 1 - sat_opacity])
        v = linear_mean([val, v], [val_opacity, 1 - val_opacity])

        raster.colors[index] = [h, s, v]

    return raster


def contrast(raster, hue_mult, sat_mult, val_mult):

    def clamp(value, lower, upper):
        return max(min(value, upper), lower)

    raster.to_hsv()

    avg_hue = hue_mean(raster)
    avg_sat = sat_mean(raster)
    avg_val = val_mean(raster)

    period_hue = 1
    period_sat = pi / min([avg_sat, 1 - avg_sat])
    period_val = pi / min([avg_val, 1 - avg_val])

    min_sat = min(raster.channel('S'))
    min_val = min(raster.channel('V'))

    # Modify each pixel
    for index, (h, s, v) in enumerate(raster.colors):

        # Blend in values at given opacity
        h = h
        s -= sin(period_sat * (s - min_sat)) * sat_mult
        v -= sin(period_val * (v - min_val)) * val_mult
        print(s)

        s = clamp(s, 0, 1)
        v = clamp(v, 0, 1)

        raster.colors[index] = [h, s, v]
    
    return raster


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
