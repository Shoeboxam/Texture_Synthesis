import json
import os

from networkx import connected_components

from Raster.Raster import Raster
from Synthesizer.images import analyze_image
from Synthesizer.cluster import spectral_cluster
from Synthesizer.metadata.network import connectivity_sort
from Utilities.vectorize import vectorize


def build(paths, image_graph):
    """Generate template json files with spectral cluster maps"""

    template_listing = []
    for bunch in connected_components(image_graph):
        bunch = connectivity_sort(bunch, image_graph)[0]
        first_image = Raster.from_path(paths.default_patches + bunch, 'RGBA')

        if first_image.shape != (16, 16):
            # TODO: Perfect place to tie in GUI generator
            continue

        try:
            template_listing.append(paths.default_patches + image_graph.node[bunch]['group_name'])
        except KeyError:
            continue

    vectorize(template_listing, make_template, (paths.template_metadata, paths.default_patches))


def make_template(template_name, template_directory, home):

    template_image = Raster.from_path(template_name, 'RGBA')
    image_clusters, guide = spectral_cluster(template_image)
    sections = len(image_clusters)

    print('-S: ' + str(len(image_clusters)) + ' | ' + template_name)

    # Analyze each cluster, save to list of dicts
    segment_metalist = []
    for ident, segment in enumerate(image_clusters):
        cluster_data = analyze_image(segment, granularity=sections)
        cluster_data['id'] = ident
        segment_metalist.append(cluster_data)

    meta_dict = {
        'group_name': template_name.replace(home, ''),
        'segment_dicts': segment_metalist,
        'cluster_map': json.dumps(guide.tolist()),
        'shape': str(template_image.shape)
    }

    # Create folder structure
    if not os.path.exists(template_directory):
        os.makedirs(template_directory)

    # Save json file
    with open(template_directory + "\\" + os.path.split(template_name)[1] + ".json", 'w') as output_file:
        json.dump(meta_dict, output_file, sort_keys=True, indent=2)
