import numpy as np
from sklearn.cluster import KMeans


def lightness_extrema(raster):
    raster.to_hsv()

    lightnesses = raster.get_opaque()[2]
    return [min(lightnesses), max(lightnesses)]


def lightness_average(raster):
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
