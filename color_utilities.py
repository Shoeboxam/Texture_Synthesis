from math import cos
from math import sin
from math import atan
from math import pi

# def hsv_to_rgb(h, s, v):

# def rgb_to_hsv(r, g, b):

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
