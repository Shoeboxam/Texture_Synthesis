from sklearn.cluster import KMeans
from utility.modular_math import *


def extrema(raster, channel):

    data = raster.channel(channel, opaque=True)
    return [min(data), max(data)]


def mean(raster, channel):
    if channel == 'H':
        return circular_mean(raster.channel(channel), raster.mask)
    else:
        return linear_mean(raster.channel(channel), raster.mask)


# RMS contrast measure
def variance(raster, channel):
    data = raster.channel(channel)
    return data.std() / linear_mean(data, raster.mask)


def color_extract(raster, color_count):
    """Pass in image path, returns X number of representative colors"""

    # Calculate X number of representative colors
    kmeans_object = KMeans(n_clusters=color_count, random_state=0)
    representative_colors = kmeans_object.fit(raster.get_opaque()).cluster_centers_
    return representative_colors
