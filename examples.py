import matplotlib.pyplot as plt

from Raster import Raster, filter, analyze
from Raster.math_utilities import *

from Minecraft import image_utilities, file_utilities


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


def break_apart():
    img = Raster.Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
    img = filter.colorize(img, 1, .1, .2, .3, .01, 0)
    img = filter.contrast(img, 0.12)

    img_set = filter.value_decomposite(img, 5)
    print(img_set)
    for index, section in enumerate(img_set):
        pil = section.get_image()
        pil.show()
        pil.save(r"C:\Users\mike_000\Desktop\pack_" + str(index) + ".png")


def open_show():
    image = Raster.Raster.from_path(r"C:\Users\mike_000\Desktop\singular.png")
    image.get_image().show()


def clusterator():
    image = Raster.Raster.from_path(
        r"C:\Users\mike_000\Desktop\tree.png")

    cluster_map = analyze.cluster(image, pieces=5)
    pieces, guide = filter.layer_decomposite(image, cluster_map)
    pieces = filter.merge_similar(pieces)

    index = 0
    for cluster in pieces:
        cluster.get_image().save(r"F:\Users\mike_000\Desktop\output\\" + str(index) + ".png")
        index += 1


def templater():
    texture_directory = r"C:\Users\mike_000\Desktop\textures"
    file_utilities.resource_filter(texture_directory)

    raster_dictionary = image_utilities.load_directory(texture_directory)

    graph = image_utilities.load_graph(r"C:\Users\mike_000\Desktop\graph_image.json")
    image_graph = image_utilities.template_extract(raster_dictionary, 0, graph)
    image_utilities.save_graph(r"C:\Users\mike_000\Desktop\graph_image.json", image_graph)

    print(image_utilities.get_templates(image_graph))