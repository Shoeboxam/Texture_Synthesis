from Minecraft import file_utilities, image_utilities, web_utilities

import json
from shutil import rmtree
from os.path import normpath, expanduser


class MinecraftSynthesizer:

    def __init__(self, config_path):
        self.config = json.load(open(config_path))
        self.home = normpath(expanduser(self.config['home']))
        self.verbose = self.config['verbose']

        self.resource_pack = self.home + '\\resource_pack\\'
        self.mods_directory = self.home + "\\mods\\"
        self.template_directory = self.home + '\\templates\\'
        self.diff_pack = self.home + '\\default_diff\\'
        self.metadata_pack = self.home + '\\default_metadata\\'
        self.output_path = self.home + '\\synthesized_resources\\'
        self.default_pack = self.home + '\\default\\'
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

        keys = image_utilities.template_reader(self.diff_pack, self.template_directory, threshold=.85)

        # # print(json.dumps(keys)) 800 504 5854

        keyfile = open('keyfile.txt', 'r')
        keyfile.write(json.dumps(keys) + "\n")

        # keys = json.loads(keyfile.readline())
        # print(keys)
        image_utilities.build_metadata_tree(self.diff_pack, self.metadata_pack, self.template_directory, keys, 5)

        # Converts json files to images with templates
        image_utilities.populate_images(self.template_directory, self.metadata_pack, self.output_path)

synthesizer = MinecraftSynthesizer(r"./config.json")

synthesizer.setup_environment()
synthesizer.create_default()
synthesizer.create_diff()
synthesizer.image_synthesis()
