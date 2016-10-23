import numpy as np
from Raster import analyze, filters
from itertools import combinations
from math import tanh
from scipy.stats.stats import pearsonr

__author__ = 'mike_000'


def spectral_cluster(template_image):
    template_image.to_hsv()

    # Intuition on how many sections to split an image into
    sections = int(max(analyze.variance(template_image)) * 50)

    if sections < 2:
        layer_map = np.zeros(np.product(template_image.shape)).astype(np.int16)
    else:
        # Clustering algorithm
        layer_map = analyze.cluster(template_image, sections)

    layer_map = np.array(layer_map).astype(int)
    image_clusters = filters.layer_decomposite(template_image, layer_map)

    return filters.merge_similar(image_clusters, layer_map=layer_map)


def difference_cluster(template_image_list):

    cluster_map_listing = []
    for image_1, image_2 in combinations(template_image_list, 2):

        difference = (image_1.colors - image_2.colors)
        difference_map = tanh(8 * difference)

        unique = True
        for cluster_map in cluster_map_listing:
            if pearsonr(cluster_map, difference_map) > .8:
                unique = False

        clustered = True
        #TODO: WHAT WAS I DOING HERE?
        #if difference_map.

        if unique and clustered:
            cluster_map_listing.append(difference_map)

    image_clusters, layer_map = 1, 1
    return image_clusters, layer_map