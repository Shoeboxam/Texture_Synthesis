from sklearn.cluster import KMeans
from scipy.stats.stats import pearsonr
from sklearn.cluster import spectral_clustering
from sklearn.feature_extraction import image
from numpy import exp
import numpy as np
from numpy.linalg.linalg import LinAlgError

from Utilities import math as math


def extrema(raster, channel):
    data = raster.channel(channel, opaque=True)
    return [min(data), max(data)]


def mean(raster, channel=None):
    if channel is None:
        return np.vectorize(mean)(raster, [letter for letter in raster.mode])

    if channel == 'H':
        return math.circular_mean(raster.channel(channel), raster.mask)
    else:
        return math.linear_mean(raster.channel(channel), raster.mask)


# RMS contrast measure
def variance(raster, channel=None):
    if channel is None:
        return np.vectorize(math.clamp)((raster.colors.T.std(axis=1) / mean(raster)))

    data = raster.channel(channel)
    return data.std() / mean(raster, channel)


def color_kmeans(raster, color_count):
    """Pass in image path, returns X number of representative colors"""
    # Cluster center
    representative_colors = []

    # Calculate X number of representative colors

    success = False

    while not success:
        try:
            kmeans_object = KMeans(n_clusters=color_count, random_state=0)
            representative_colors = kmeans_object.fit(raster.get_opaque()).cluster_centers_
            success = True
        except ValueError:
            color_count -= 1
        except OverflowError:
            print(color_count)
            pass

    return np.vectorize(math.clamp)(representative_colors)


def color_extract(raster, color_count):
    raster.to_hsv()
    opaque_data = raster.get_opaque().T
    print(opaque_data)
    hues = math.circular_sort(opaque_data[0])
    sats = sorted(opaque_data[1])
    vals = sorted(opaque_data[2])

    colors = []
    step_size = len(hues) / color_count

    for i in range(color_count):
        colors.append((hues[int(i*step_size)], sats[int(i*step_size)], vals[int(i*step_size)]))
    return colors


def correlate(a, b):
    if len(a.colors) != len(b.colors):
        return 0

    if pearsonr(a.mask, b.mask)[0] > .99:
        return pearsonr(a.channel('V'), b.channel('V'))[0]
    return 0


def cluster(raster, pieces):
    raster.to_hsv()
    graph = image.img_to_graph(raster.get_tiered())

    beta = 15
    graph.data = exp(-beta * graph.data / raster.get_opaque().std())

    labels = []
    success = False

    while not success:
        try:
            labels = spectral_clustering(graph, n_clusters=pieces, assign_labels='discretize', random_state=1)
            success = True
        except (LinAlgError, ValueError):
            pieces -=1

            # If clustering is non-convergent, return single cluster
            if pieces == 0:
                return np.zeros(np.product(raster.shape))

    return labels.reshape(raster.with_alpha().shape)[:, 0]
