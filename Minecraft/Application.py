from Minecraft import file_utilities, image_utilities, web_utilities, metadata_utilities

import json
from shutil import rmtree
from os.path import normpath, expanduser
import os

class MinecraftSynthesizer:

    def __init__(self, config_path):
        self.config = json.load(open(config_path))
        self.verbose = self.config['verbose']

        self.home = normpath(expanduser(self.config['home']))

        self.resource_pack = self.home + '\\resource_pack\\'
        self.default_pack = self.home + '\\default_pack\\'
        self.mods_directory = self.home + "\\mods\\"

        self.template_directory = self.home + '\\templates\\'
        self.template_directory_autogen = self.home + '\\metadata\\templates_autogen\\'

        self.diff_pack = self.home + '\\default_diff\\'
        self.file_metadata = self.home + '\\metadata\mappings\\'
        self.template_metadata = self.home + '\\metadata\templates\\'

        self.output_path = self.home + '\\synthesized_resources\\'
        self.key_repository = self.home + '\\key_repository\\'

        self.setup_environment()

    def setup_environment(self):
        web_utilities.clone_repo(self.config['resource_pack'], self.resource_pack)
        web_utilities.clone_repo(self.config['key_repository'], self.key_repository)

    def create_default(self):
        """Creates a default texture pack in mod repository format"""

        temp_pack = self.home + "\\resource_temp\\"

        # Create staging pack
        file_utilities.extract_files(self.mods_directory, temp_pack)
        file_utilities.resource_filter(temp_pack)

        # Convert to repo format and output to default pack path
        file_utilities.repository_format(temp_pack, self.default_pack, self.key_repository)

        # Delete staging pack
        rmtree(temp_pack, True)

    def create_diff(self):
        """Creates a pack of untextured files in mod repository format"""

        # Gets a list of textures that have not been made via file diff
        untextured_paths = file_utilities.get_untextured(self.resource_pack, self.default_pack)

        # Create a pack with the untextured files
        file_utilities.copytree_wrapper(self.default_pack, self.diff_pack, untextured_paths)
        file_utilities.resource_filter(self.diff_pack)

    def update_metadata(self):
        # Load all images into memory
        raster_dictionary = metadata_utilities.load_directory(self.default_pack)
        print("Loaded default images.")

        # Group images together/organize into graph
        image_graph = metadata_utilities.load_graph(self.home + '\\image_graph.json')
        # image_graph = metadata_utilities.network_images(raster_dictionary, threshold=0)
        # metadata_utilities.save_graph(self.home + '\\image_graph.json', image_graph)
        print("Updated image graph.")

        # Create informational json files for templates and files
        metadata_utilities.template_metadata(self.template_directory_autogen, image_graph, raster_dictionary)
        metadata_utilities.file_metadata(self.file_metadata, self.template_directory_autogen, image_graph, raster_dictionary)
        print("Created JSON metadata files.")


    def synthesize(self):
        """Extract representative colors for every image that matches template"""

        # Update template directory
        template_paths = metadata_utilities.connectivity_sort(image_graph)


        image_utilities.prepare_templates(
            self.default_pack, self.resource_pack, template_paths, self.template_directory_autogen)
        print("Wrote additions to templates.")

        key_dict = image_utilities.template_reader(template_paths, image_graph)

        # Converts json files to images with templates
        image_utilities.populate_images(self.template_directory, self.file_metadata, self.output_path)


if __name__ == '__main__':
    synthesizer = MinecraftSynthesizer(r"./config.json")

    # synthesizer.create_default()
    # synthesizer.create_diff()
    synthesizer.update_metadata()
