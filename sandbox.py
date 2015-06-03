import matplotlib.pyplot as plt

from Raster import Raster, filter, analyze
from Utility.math_utilities import *


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
    img = Raster.Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
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
    image = Raster.Raster.from_path(r"C:\Users\mike_000\Desktop\singular.png")
    image.get_image().show()


def vander_matrix():
    y = sorted(np.random.rand(7, 1).flatten())
    x = sorted(np.random.rand(7, 1).flatten())
    print(y)
    plt.scatter(x, y)

    test_bank = np.linspace(min(x), max(x), 50)

    poly = polysolve(polyfit(x, y), test_bank)
    plt.plot(test_bank, poly)

    plt.show()


def spectral_decomp():
    image = Raster.Raster.from_path(
        r"F:\Users\mike_000\Textures\Invictus_Textures\assets\minecraft\textures\items\bed.png")

    cluster_map = analyze.cluster(image, pieces=5)
    pieces, guide = filter.layer_decomposite(image, cluster_map)
    pieces = filter.merge_similar(pieces)

    index = 0
    for cluster in pieces:
        cluster.get_image().save(r"F:\Users\mike_000\Desktop\output\\" + str(index) + ".png")
        index += 1
