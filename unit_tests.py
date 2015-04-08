from Raster import Raster
from Filters import *
from color_utilities import *

import matplotlib.pyplot as plt
import numpy as np

np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)


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


def alpha_mask_test():
    arr = np.zeros((100, 4))
    arr[:, 0] = .5
    arr[:, 1] = .0
    arr[:, 2] = np.linspace(0, 1, 100)
    arr[:, 3] = 1.
    arr = np.reshape(arr, (10, 10, 4))
    img = Raster.from_array(arr, 'HSV')
    img_list = image_decompose(img, 2)

    for index, section in enumerate(img_list):
        rgb_img = section
        rgb_img.to_rgb()
        PIL = rgb_img.get_image()
        PIL.save(r"C:\Users\mike_000\Desktop\pack_" + str(index) + ".png")

# alpha_mask_test()


def image_process():
    img = Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
    img = colorize(img, 1, .1, .2, .3, .01, 0)
    img = contrast(img, 1, .2, 0.12)

    img_set = image_decompose(img, 5)
    print(img_set)
    for index, section in enumerate(img_set):
        PIL = section.get_image()
        PIL.show()
        PIL.save(r"C:\Users\mike_000\Desktop\pack_" + str(index) + ".png")
    PIL = img.get_image()

    # Tester
    print(circular_mean((.23, .51, .98)))


def recompose():
    arr = np.zeros((100, 4))
    arr[:, 0] = .5
    arr[:, 1] = .0
    arr[:, 2] = np.linspace(.5, 1, 100)
    arr[:, 3] = 1.
    arr = np.reshape(arr, (10, 10, 4))
    img = Raster.from_array(arr, 'HSV')

    img_list = image_decompose(img, 5)

    for index, img in enumerate(img_list):
        img.get_image().save(r"C:\Users\mike_000\Desktop\recombined_" + str(index) + ".png")
    recombined = image_composite(img_list)

    recombined.get_image().save(r"C:\Users\mike_000\Desktop\recombined.png")
recompose() 