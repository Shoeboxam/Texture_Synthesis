from sklearn.cluster import KMeans
from scipy.stats.stats import pearsonr
from Utility import math_utilities as math

from sklearn.cluster import spectral_clustering
from sklearn.feature_extraction import image


def extrema(raster, channel):
    data = raster.channel(channel, opaque=True)
    return [min(data), max(data)]


def mean(raster, channel):
    if channel == 'H':
        return math.circular_mean(raster.channel(channel), raster.mask)
    else:
        return math.linear_mean(raster.channel(channel), raster.mask)


# RMS contrast measure
def variance(raster, channel):
    data = raster.channel(channel)
    return data.std() / math.linear_mean(data, raster.mask)


def color_extract(raster, color_count):
    """Pass in image path, returns X number of representative colors"""

    # Calculate X number of representative colors
    kmeans_object = KMeans(n_clusters=color_count, random_state=0)
    representative_colors = kmeans_object.fit(raster.get_opaque()).cluster_centers_
    return representative_colors


def correlate(a, b):
    if len(a.colors) != len(b.colors):
        return 0

    if pearsonr(a.mask, b.mask)[0] > .99:
        return pearsonr(a.channel('V'), b.channel('V'))[0]
    return 0


def cluster(raster, pieces):
    graph = image.img_to_graph(raster.get_tiered())

    beta = 5
    graph.data = np.exp(-beta * graph.data / raster.get_opaque().std())

    labels = spectral_clustering(graph, n_clusters=pieces,
                                 assign_labels='discretize',
                                 random_state=1)

    return labels.reshape(raster.with_alpha().shape)[:, 0]