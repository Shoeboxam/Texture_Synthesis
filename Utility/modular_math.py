from math import cos
from math import sin
from math import atan
from math import pi
import numpy as np

# def hsv_to_rgb(h, s, v):

# def rgb_to_hsv(r, g, b):


def clamp(value, lower=0., upper=1.):
        return max(min(value, upper), lower)


def smooth_hill(minima, maxima, value):
    '''Map value to sinusoidal wave with period start/end at given extrema in range of 0 to 1'''

    period = (2 * pi) / (maxima - minima)
    return 1 - (cos(period * (value - minima)) * .5 + .5)


def smooth_hole(minima, maxima, value):
    period = (2 * pi) / (maxima - minima)
    return cos(period * (value - minima)) * .5 + .5


def smooth_rise(minima, maxima, value):
    period = pi / (maxima - minima)
    return 1 - (cos(period * (value - minima)) * .5 + .5)


def smooth_fall(minima, maxima, value):
    period = pi / (maxima - minima)
    return cos(period * (value - minima)) * .5 + .5


def linear_mean(values, weights=None):
    if weights is None:
        # print("No weights")
        weights = [1] * len(values)

    # Total of 1
    normalized_weights = np.array(weights) / float(sum(weights))
    # print("Val: " + str(values))
    # print("Wts: " + str(normalized_weights))
    # print("Equ: " + str(np.dot(values, normalized_weights)))

    # Multiply channel values with their weights, then add together via dot product
    return np.dot(values, normalized_weights)


# Computes weighted circular average
def circular_mean(values, weights=None):
    # Range of 0 to 1

    if weights is None:
        weights = [1] * len(values)

    # Scale to radians
    period = 2 * pi

    x = []
    y = []

    # normalize weights such that the products total to one
    normalizer = sum(weights)

    for val, weight in zip(values, weights):
        x.append(cos(val * period) * weight / normalizer)
        y.append(sin(val * period) * weight / normalizer)
    try:
        offset = (atan(sum(y) / sum(x))) / period
    # Catch Undefined tan(90) and tan(270)
    except ZeroDivisionError:
        try:
            offset = sum(values) / len(values)
        except:
            offset = 0.

    # Adjust domain of offset
    # print("Xes: " + str(x))
    if sum(x) < 0:
        offset += .5

    # Due to sinusoidal nature and period of one, ...
    # mod does not change val, it merely sets a range
    return offset % 1


def circular_sort(hues):
    hues = sorted(hues)

    hue_mean = circular_mean(hues)
    hue_mean += .5
    hue_mean %= 1.

    first_index = 0
    # Find first index in listing
    for index, value in enumerate(hues):
        if value >= hue_mean:
            first_index = index
            break

    sorted_hues = []
    for index in range(len(hues)):
        sorted_hues.append(hues[(first_index + index) % len(hues)])

    return sorted_hues
