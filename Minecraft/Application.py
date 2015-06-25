from Minecraft import file_utilities, image_utilities, web_utilities, metadata_utilities

import json
from os.path import normpath, expanduser
import os
import shutil


class MinecraftSynthesizer:

    def __init__(self, config_path):
        self.config = json.load(open(config_path))
        self.verbose = self.config['verbose']
        self.home = normpath(expanduser(self.config['home']))

        self.vanilla_pack = self.home + '\\sources\\vanilla_pack\\'
        self.resource_pack = self.home + '\\sources\\resource_pack\\'
        self.key_repository = self.home + '\\sources\\key_repository\\'
        self.mods_directory = self.home + '\\sources\\mods\\'

        self.default_patches = self.home + '\\staging\\default_patches\\'
        self.repository_patches = self.home + '\\staging\\repository_patches\\'
        self.untextured_patches = self.home + '\\staging\\untextured_patches\\'

        self.template_metadata = self.home + '\\metadata\\templates\\'
        self.file_metadata = self.home + '\\metadata\\mappings\\'
        self.image_network_path = self.home + '\\metadata\\image_graph.json'

        self.output_path = self.home + '\\output\\synthesized_resources\\'

        web_utilities.download_minecraft(
            self.config['mc_version'], os.path.normpath(self.vanilla_pack))

        web_utilities.clone_repo(self.config['resource_pack'], self.resource_pack)

        web_utilities.clone_repo(self.config['key_repository'], self.key_repository)
        print('Sources installed')

        try:
            os.makedirs(self.home + '\\metadata')
        except FileExistsError:
            pass

    def create_default(self):
        """Creates a default texture pack in mod repository format"""

        # Create staging pack
        file_utilities.extract_files(self.mods_directory, self.default_patches)
        shutil.copy(os.path.normpath(self.vanilla_pack), self.default_patches + '\\minecraft\\')
        print('Unpacked mods')

        file_utilities.resource_filter(self.default_patches)
        print('Isolated image files')

        file_utilities.repository_format(self.default_patches, self.repository_patches, self.key_repository)
        print('Extracted repository matches')

    def create_untextured(self):
        """Creates a pack of untextured files in mod repository format"""

        # Gets a list of textures that have not been made via file diff
        untextured_paths = file_utilities.get_untextured(self.key_repository, self.repository_patches)
        print(untextured_paths)

        # Create a pack with the untextured files
        file_utilities.copy_filter(self.default_patches, self.untextured_patches, untextured_paths)

    def update_metadata(self):

        # Load all images into memory
        raster_dictionary = metadata_utilities.load_directory(self.default_patches)
        print("Loaded default images.")

        # Group images together/organize into graph
        image_graph = metadata_utilities.load_graph(self.image_network_path)

        for image_grouping in raster_dictionary.values():
            image_graph = metadata_utilities.network_images(image_grouping, threshold=0, network=image_graph)

        metadata_utilities.save_graph(self.image_network_path, image_graph)
        print("Updated image graph.")

        # Create informational json files for templates and files
        metadata_utilities.template_metadata(self.template_metadata, image_graph, raster_dictionary)
        metadata_utilities.file_metadata(
            self.file_metadata, self.template_metadata, image_graph, raster_dictionary)
        print("Created JSON metadata files.")

    def synthesize(self):
        """Extract representative colors for every image that matches template"""

        # Update template directory
        image_graph = metadata_utilities.load_graph(self.home + '\\metadata\\image_graph.json')
        template_paths = metadata_utilities.connectivity_sort(image_graph)

        image_utilities.prepare_templates(
            self.untextured_patches, self.resource_pack, template_paths, self.template_metadata)
        print("Wrote additions to templates.")

        key_dict = image_utilities.template_reader(template_paths, image_graph)

        # Converts json files to images with templates
        image_utilities.populate_images(self.template_metadata, self.file_metadata, self.output_path)


if __name__ == '__main__':
    synthesizer = MinecraftSynthesizer(r"./config.json")

    synthesizer.create_default()
    synthesizer.create_untextured()
    synthesizer.update_metadata()
