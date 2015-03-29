from math import cos
from math import sin
from math import atan
from math import pi

# def hsv_to_rgb(h, s, v):

# def rgb_to_hsv(r, g, b):

def linear_mean(values, weights=None):
    if weights is None:
        weights = [1] * len(values)

    # Total of 1
    normalized_weights = weights / weights.sum()

    # Multiply channel values with their weights, then add together
    return (values * normalized_weights).sum()


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
        offset = sum(values) / len(values)

    # Adjust domain of offset
    if sum(x) < 0:
        offset += .5

    # Due to sinusoidal nature and period of one, ...
    # mod does not change val, it merely sets a range
    return offset % 1
