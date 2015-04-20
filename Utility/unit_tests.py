import matplotlib.pyplot as plt

from raster import Raster, filter
from utility.modular_math import *

np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
np.set_printoptions(threshold=np.nan)


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


def image_process():
    img = Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
    img = filter.colorize(img, 1, .1, .2, .3, .01, 0)
    img = filter.contrast(img, 0.12)

    img_set = filter.decomposite(img, 5)
    print(img_set)
    for index, section in enumerate(img_set):
        pil = section.get_image()
        pil.show()
        pil.save(r"C:\Users\mike_000\Desktop\pack_" + str(index) + ".png")

    # Tester
    print(circular_mean((.23, .51, .98)))


def open_show():
    image = Raster.from_path(r"C:\Users\mike_000\Desktop\singular.png")
    image.get_image().show()
open_show()