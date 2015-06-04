from Minecraft import file_utilities, image_utilities, web_utilities

import json
from shutil import rmtree
from os.path import normpath, expanduser


class MinecraftSynthesizer:

    def __init__(self, config_path):
        self.config = json.load(open(config_path))
        self.verbose = self.config['verbose']

        self.home = normpath(expanduser(self.config['home']))

        self.resource_pack = self.home + '\\resource_pack\\'
        self.default_pack = self.home + '\\default_pack\\'
        self.mods_directory = self.home + "\\mods\\"

        self.template_directory = self.home + '\\templates\\'
        self.template_directory_autogen = self.home + '\\templates_autogen\\'

        self.diff_pack = self.home + '\\default_diff\\'
        self.metadata_pack = self.home + '\\default_metadata\\'

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

    def image_synthesis(self):
        """Extract representative colors for every image that matches template"""

        # Load all images into memory
        # raster_dictionary = image_utilities.load_directory(self.default_pack)

        # Find templates from loaded images
        image_graph = image_utilities.load_graph(self.home + '\\image_graph.json')
        # image_graph = image_utilities.template_extract(raster_dictionary, threshold=0, network=image_graph)
        # image_utilities.save_graph(self.home + '\\image_graph.json', image_graph)

        template_paths = image_utilities.get_templates(image_graph)

        image_utilities.prepare_templates(
            self.default_pack, self.resource_pack, template_paths, self.template_directory_autogen)

        # image_utilities.build_metadata_tree(self.diff_pack, self.metadata_pack, self.template_directory_autogen, keys, 5)
        #
        # # Converts json files to images with templates
        # image_utilities.populate_images(self.template_directory, self.metadata_pack, self.output_path)

synthesizer = MinecraftSynthesizer(r"./config.json")

# synthesizer.create_default()
# synthesizer.create_diff()
synthesizer.image_synthesis()
