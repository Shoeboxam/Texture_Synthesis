import os

from networkx import connected_component_subgraphs

from Synthesizer import images, metadata
from Synthesizer.settings import Settings
import Synthesizer.Metadata.network

import json


def update_metadata(paths):

    # Weakly group images to partition image set size- crucial optimization step
    if os.path.exists(paths.home + '//metadata//preprocess.json'):
        clumped_paths = json.loads(open(paths.home + '//metadata//preprocess.json').read())
        # clumped_paths = metadata_utilities.image_hash(paths.default_patches, init=clumped_paths)
    else:
        clumped_paths = Synthesizer.Metadata.network.image_hash(paths.default_patches)
    print("Hashed source images")

    with open(paths.home + '//metadata//preprocess.json', 'w') as json_file:
        json.dump(clumped_paths, json_file)

    # Combinatorial image grouping to graph
    image_graph = Synthesizer.Metadata.network.load_graph(paths.image_network_path)

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
    metadata.analyze.template_metadata(paths.template_metadata, paths.default_patches, image_graph)
    metadata.metadata.file_metadata(paths.file_metadata, paths.template_metadata, paths.default_patches, image_graph)
    print("Created JSON metadata files.")

def synthesize(paths):
    """Extract representative colors for every image that matches template"""

    # Update template directory
    image_graph = Synthesizer.Metadata.network.load_graph(paths.home + '\\metadata\\image_graph.json')

    template_paths = []

    def template_selection(paths):
        for node in paths:
            if os.path.exists(paths.resource_pack + '\\' + os.path.join(*(node.split(os.path.sep)[1:]))):
                template_paths.append(node)
                return

    for bunch in connected_component_subgraphs(image_graph):
        sorted_bunch = Synthesizer.Metadata.network.connectivity_sort(bunch.nodes(), bunch)

        if len(sorted_bunch) == 1:
            continue

        template_selection(sorted_bunch)

    print(str(len(template_paths)) + ' templates identified.')

    images.prepare_templates(
        paths.untextured_patches, paths.resource_pack, template_paths, paths.template_metadata)
    print("Wrote additions to templates.")

    if not os.path.exists(paths.bindings_metadata):
        os.mkdir(paths.bindings_metadata)

    # key_dict = image_utilities.template_reader(template_paths, image_graph)

    # Converts json files to images with templates
    images.populate_images(
        paths.default_patches, paths.bindings_metadata, paths.file_metadata, paths.output_path)


if __name__ == '__main__':
    repository = Settings(r"./config.json")

    # Synthesizer.files.create_default(repository)
    # create_untextured(repository)
    # update_metadata(repository)

    synthesize(repository)
