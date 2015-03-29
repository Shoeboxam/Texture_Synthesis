import numpy as np
from sklearn.cluster import KMeans

from color_utilities import *

# TODO: Factor alpha into means

def lightness_extrema(raster):
    raster.to_hsv()

    lightnesses = raster.get_opaque()[2]
    return [min(lightnesses), max(lightnesses)]


def hue_mean(raster):
    raster.to_hsv()

    hues = raster.get_opaque()[0]
    return circular_mean(hues, raster.mask)


def sat_mean(raster):
    raster.to_hsv()

    sats = raster.get_opaque()[1]
    return sum(sats) / len(sats)


def val_mean(raster):
    raster.to_hsv()

    lightnesses = raster.get_opaque()[2]
    return sum(lightnesses) / len(lightnesses)


def lightness_deviation(raster):
    raster.to_hsv()
    lightnesses = raster.get_opaque()[2]

    return lightnesses.std()


def color_extract(raster, color_count):
    """Pass in image path, returns X number of representative colors"""

    # Calculate X number of representative colors
    KMeans_object = KMeans(n_clusters=color_count, random_state=0)
    representative_colors = KMeans_object.fit(raster.get_opaque()).cluster_centers_
    return representative_colors.astype(int)


# Computes weighted circular average
def mean_hue(hues, weights=None):
    # Range of 0 to 1

    if weights is None:
        weights = [1] * len(hues)

    # Scale to radians
    period = 2 * pi

    x = []
    y = []

    # normalize weights such that the products total to one
    normalizer = sum(weights)

    for hue, weight in zip(hues, weights):
        x.append(cos(hue * period) * weight / normalizer)
        y.append(sin(hue * period) * weight / normalizer)

    try:
        offset = (atan(sum(y) / sum(x))) / period
    # Catch Undefined tan(90) and tan(270)
    except ZeroDivisionError:
        offset = sum(hues) / len(hues)

    # Adjust domain of offset
    if sum(x) < 0:
        offset += .5

    # Due to sinusoidal nature and period of one, ...
    # mod does not change hue, it merely sets a range
    return offset % 1