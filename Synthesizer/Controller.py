import os
from itertools import chain

from networkx import connected_component_subgraphs

from Synthesizer import images, metadata
from Synthesizer.settings import Settings

import Synthesizer.metadata.templates as templates
import Synthesizer.metadata.network as network
import Synthesizer.metadata.mappings as mappings
import Synthesizer.metadata.bindings as bindings

import json


def global_metadata(paths):
    """Generate metadata for default graphics"""

    # Weakly group images to partition image set size- crucial optimization step
    if os.path.exists(paths.image_preprocess):
        clumped_paths = json.loads(open(paths.image_preprocess).read())
    else:
        clumped_paths = network.alpha_categorize(paths)
    print("Hashed source images")

    with open(paths.image_preprocess, 'w') as json_file:
        json.dump(clumped_paths, json_file)

    # Combinatorial image grouping to graph
    image_graph = network.load_graph(paths.image_network_path)

    total = len(list(chain(*clumped_paths.values())))
    counter = 0.

    for image_paths in clumped_paths.values():
        counter += len(image_paths)
        print(str(int(counter / float(total) * 100)) + "% complete")

        if len(image_paths) > 1:
            image_grouping = images.load_paths(paths.default_patches, image_paths)
            image_graph = metadata.network.network_images(
                image_grouping, threshold=0, network=image_graph)
        else:
            image_graph.add_node(image_paths[0])

    metadata.network.save_graph(paths.image_network_path, image_graph)
    print("Updated image graph.")

    # Create informational json files for templates and files
    templates.build(paths, image_graph)
    mappings.build(paths, image_graph)
    print("Created JSON metadata files.")


def local_metadata(paths):
    """Generate metadata specific to given resource pack"""

    # Update template directory
    image_graph = network.load_graph(paths.home + '\\metadata\\image_graph.json')

    template_paths = []

    def template_selection(path_listing):
        for node in path_listing:
            if os.path.exists(path_listing.resource_pack + '\\' + os.path.join(*(node.split(os.path.sep)[1:]))):
                template_paths.append(node)
                return

    for bunch in connected_component_subgraphs(image_graph):
        sorted_bunch = network.connectivity_sort(bunch.nodes(), bunch)

        if len(sorted_bunch) == 1:
            continue

        template_selection(sorted_bunch)

    print(str(len(template_paths)) + ' templates identified.')

    bindings.build(paths, template_paths)


def synthesize(paths):
    # Converts json files to images with templates
    images.populate_images(paths)


if __name__ == '__main__':
    repository = Settings(r"./config.json")

    # files.create_default(repository)
    # create_untextured(repository)
    # update_metadata(repository)

    synthesize(repository)
