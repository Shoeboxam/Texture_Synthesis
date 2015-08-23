import ast
import json
import os

from networkx import connected_components

from Raster import filters as filter_raster
from Raster.Raster import Raster
from Synthesizer.images import analyze_image


def metadata_mappings(output_directory, template_directory, source_directory, image_graph, sections=3):
    """Save representative data to json files in meta pack"""
    if not os.path.exists(template_directory):
        os.makedirs(template_directory)

    template_data = {}
    for json_filename in os.listdir(template_directory):
        with open(template_directory + json_filename, 'r') as json_file:
            json_data = json.load(json_file)
            template_data[json_data['group_name']] = json_data

    # Retrieve the relevant info for every texture
    keys = {}
    for bunch in [i for i in connected_components(image_graph) if len(i) > 1]:
        for node in bunch:
            Raster.from_path(source_directory + node, 'RGBA')
            keys[node] = image_graph.node[node]['group_name'], Raster.from_path(source_directory + node, 'RGBA')

    # Iterate through each file that is part of the key
    for key, (template_name, default_image) in keys.items():

        # Load corresponding cluster map
        try:
            with open(template_directory + "\\" + os.path.split(template_name)[1] + ".json", 'r') as config:
                layer_map = ast.literal_eval(json.load(config)['cluster_map'])
        except FileNotFoundError:
            print("Could not find: " + template_directory + "\\" + os.path.split(template_name)[1] + ".json")
            continue

        # Use corresponding cluster map to break image into pieces
        try:
            image_clusters = filter_raster.layer_decomposite(default_image, layer_map)
        except ValueError:
            continue
        templ_clusters = filter_raster.layer_decomposite(
            Raster.from_path(source_directory + template_name, 'RGBA'), layer_map)

        # Analyze each cluster
        segment_metalist = []
        for ident, (segment, template_segment) in enumerate(zip(image_clusters, templ_clusters)):
            segment_data = analyze_image(segment, template_segment, sections)
            segment_data['id'] = ident
            segment_metalist.append(segment_data)

        meta_dict = {
            'group_name': template_name,
            'segment_dicts': segment_metalist
        }

        output_path = os.path.split(output_directory + key)[0]

        # Create folder structure
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Save json file
        with open(output_path + "\\" + os.path.split(key)[1] + ".json", 'w') as output_file:
            json.dump(meta_dict, output_file, sort_keys=True, indent=2)
