import matplotlib.pyplot as plt

from raster import raster, filter, analyze
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
    img = raster.Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
    img = filter.colorize(img, 1, .1, .2, .3, .01, 0)
    img = filter.contrast(img, 0.12)

    img_set = filter.value_decomposite(img, 5)
    print(img_set)
    for index, section in enumerate(img_set):
        pil = section.get_image()
        pil.show()
        pil.save(r"C:\Users\mike_000\Desktop\pack_" + str(index) + ".png")

    # Tester
    print(circular_mean((.23, .51, .98)))


def open_show():
    image = raster.Raster.from_path(r"C:\Users\mike_000\Desktop\singular.png")
    image.get_image().show()


def vander_matrix():
    analyze.best_fit_vandermonde((1,2,3,4), 0)


def specular():
    image = raster.Raster.from_path(r"C:\Users\mike_000\Textures\Invictus_Textures\assets\minecraft\textures\items\diamond_axe.png")
    pieces = filter.spectral_cluster(image)

    index = 0
    for cluster in pieces:
        cluster.get_image().save("C:\Users\mike_000\Desktop\output\\" + str(index )+ ".png")
        index += 1

specular()