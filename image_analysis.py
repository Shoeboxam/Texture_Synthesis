from sklearn.cluster import KMeans
from math_utilities import *


def lightness_extrema(raster):
    raster.to_hsv()

    lightnesses = raster.get_opaque()[:, 2]
    # print(lightnesses)
    return [min(lightnesses), max(lightnesses)]


def hue_mean(raster):
    raster.to_hsv()

    hues = raster.get_opaque()

    return circular_mean(hues, raster.mask)


def sat_mean(raster):
    raster.to_hsv()
    return linear_mean(raster.channel('S'), raster.mask)


def val_mean(raster):
    raster.to_hsv()
    return linear_mean(raster.channel('V'), raster.mask)


# RMS contrast measure
def lightness_variance(raster):
    raster.to_hsv()
    lightnesses = raster.channel('V')

    return lightnesses.std() / linear_mean(lightnesses, raster.mask)


def color_extract(raster, color_count):
    """Pass in image path, returns X number of representative colors"""

    # Calculate X number of representative colors
    KMeans_object = KMeans(n_clusters=color_count, random_state=0)
    representative_colors = KMeans_object.fit(raster.get_opaque()).cluster_centers_
    return representative_colors
