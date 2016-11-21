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

    def doubleMADsfromMedian(y, thresh=3.5):
        m = np.median(y)
        abs_dev = np.abs(y - m)
        left_mad = np.median(abs_dev[y <= m])
        right_mad = np.median(abs_dev[y >= m])
        y_mad = left_mad * np.ones(len(y))
        y_mad[y > m] = right_mad

        modified_z_score = 0.6745 * abs_dev / y_mad
        modified_z_score[y == m] = 0
        y[modified_z_score > thresh] = m
        return sorted(y)

    raster.to_hsv()
    opaque_data = raster.get_opaque().T
    step_size = int(len(opaque_data[0]) / color_count)
    if (step_size == 0):
        step_size += 1
    mean_hue = math.circular_mean(opaque_data[0])
    normalized_hues = np.mod(np.add(opaque_data[0,::step_size], (0.5 - mean_hue)), 1)

    hues = np.mod(doubleMADsfromMedian(np.add(normalized_hues, mean_hue - 0.5)), 1)
    sats = doubleMADsfromMedian(opaque_data[1,::step_size])
    vals = doubleMADsfromMedian(opaque_data[2,::step_size])

    return np.array((hues, sats, vals))


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
