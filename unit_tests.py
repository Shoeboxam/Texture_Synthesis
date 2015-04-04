from Raster import Raster
from Filters import *
from color_utilities import *

import matplotlib.pyplot as plt
import numpy as np


def smooth_point():
    minima = 0.399
    maxima = 0.42

    brightnesses = np.linspace(minima, maxima, 100)
    outputs = []

    for bright in brightnesses:
        outputs.append(smooth_hill(minima, maxima, bright))

    plt.plot(brightnesses, outputs)
    plt.axis((minima, maxima, 0, 1))

    plt.show()


img = Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
img = colorize(img, 1, .5, .2, .3, .01, 0)
img = contrast(img, 1, .08, 0.12)
PIL = img.get_image()

# Tester
print(circular_mean((.23, .51, .98)))

PIL.show()
