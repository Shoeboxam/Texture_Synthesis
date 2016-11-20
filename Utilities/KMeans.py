import random
from Utilities import math
import numpy as np
import matplotlib.pyplot as plt


class KMeans(object):

    def __init__(self, k, data=None, seeds=None):
        self.k = k
        self.data = data
        self.seeds = seeds
        self.clusters = {}
        self.centroids = [random.uniform(0, 1) for x in range(k)]
        self.new_centroids = [random.uniform(0, 1) for x in range(k)]

    def fit(self):
        while not set(self.centroids) == set(self.new_centroids):  # check for convergence
            self.centroids = self.new_centroids
            self.clusters = self.classify_points()
            self.new_centroids = self.find_centroids()

    def classify_points(self):
        clusters = {}
        for point in self.data:
            key = min([(i, math.cylindrical_norm(point, cent)) for i, cent in enumerate(self.centroids)], key=lambda t:t[1])[0]
            try:
                clusters[key].append(key)
            except KeyError:
                clusters[key] = [key]
        return clusters

    def find_centroids(self):
        mu = []
        keys = sorted(self.clusters.keys())

        for key in keys:
            channel_data = np.array(self.clusters[key]).transpose()
            print(channel_data)
            hue_mean = math.circular_mean(channel_data[0])
            sat_mean = math.linear_mean(channel_data[1])
            val_mean = math.linear_mean(channel_data[2])
            mu.append((hue_mean, sat_mean, val_mean))

        return mu

    def SSE(self):
        return 1


def minimize_deviance(points, k):

    kmodel = []
    kerror = []
    for i in range(k):
        kinst = KMeans(i, points)
        kinst.fit()
        kmodel.append(kinst)
        kerror.append(kinst.SSE())

    poly = np.polyfit(range(k), kerror, 3)
    inflections = np.roots(np.polyder(poly, 2))

    for inflect in inflections:
        print(np.polyval(poly, inflect))

    plt.plot(range(k), kerror, )
    plt.plot()
    plt.show()
