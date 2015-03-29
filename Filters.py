import numpy as np
from image_analysis import *
from color_utilities import *


def colorize(raster, hue, sat, val, hue_opacity=1., sat_opacity=.5, val_opacity=.5):

    raster.to_hsv()

    for index, (h, s, v) in enumerate(raster.colors):
        h = mean_hue([h, hue], [hue_opacity, 1 - hue_opacity])
        print(h)
        s = (sat * sat_opacity) + s * (1 - sat_opacity)
        v = (val * val_opacity) + v * (1 - val_opacity)
        raster.colors[index] = [h, s, v]

    return raster


def contrast(raster, hue, sat, val, hue_opacity=1., sat_opacity=.5, val_opacity=.5):

    return

def image_decompose(raster, layers):
    """Slice image by a given number of lightness zones"""

    minimum, maximum = lightness_extrema(raster)

    raster_components = []
    for layer in range(layers):
        # CREATE MASK
        mask

        # APPLY MASK
        raster_components.append(mask_alpha(raster, mask))


def mask_alpha(raster, mask):
    for index, ((r, g, b, a), transparency) in enumerate(zip(raster.pixels, mask)):
        raster.pixels[index] = [r, g, b, a * transparency]

    return raster


def image_composite(raster_list):
    """Combine all input layers with additive alpha blending"""

    # Results for each pixel is added to canvas
    canvas = Raster(0, width, height, 'rgb').to_hsv()

    # Take transpose of pixel layers to produce a list of corresponding pixels
    for pixel_profile in np.array(zip(*pixel_layers)):

        # Opacity is the sum of alpha channels
        opacity = sum(pixel_list[:, 0])

        # If one of the pixels has opacity
        if opacity != 0:
            pixel = []

            # Calculate weights for each pixel's colors based on alpha strength between 0 and 1
            opacity_weight_sum = pixel_list[:, 3].sum()
            normalized_opacity_weights = pixel_list[:, 3] / opacity_weight_sum

            # Multiply channel values with their weights, then add together
            pixel.append((pixel_list[:, 0] * normalized_opacity_weights).sum())
            pixel.append((pixel_list[:, 1] * normalized_opacity_weights).sum())
            pixel.append((pixel_list[:, 2] * normalized_opacity_weights).sum())
            pixel.append(opacity)
            canvas.append(pixel)
        else:
            canvas.append([0, 0, 0, 0])

    pixels = (np.array(canvas)).astype(np.uint8)
    pixels = np.reshape(pixels, (width, height, 4))
    return Image.fromarray(np.ascontiguousarray(pixels), mode='RGBA')
