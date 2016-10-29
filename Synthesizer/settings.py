import json
from os.path import normpath, expanduser
from os import makedirs

from Synthesizer.sources import web


class Settings:

    def __init__(self, config_path):
        self.config = json.load(open(config_path))
        self.verbose = self.config['verbose']
        self.home = normpath(expanduser(self.config['home']))

        self.vanilla_pack = self.home + '\\sources\\vanilla_pack\\'
        self.resource_pack = self.home + '\\sources\\resource_pack\\'
        self.key_repository = self.home + '\\sources\\key_repository\\'
        self.mods_directory = self.home + '\\sources\\mods\\'
        self.resource_skeletons = self.home + '\\sources\\resource_skeletons\\'

        self.stencil_editing = self.home + '\\staging\\stencil_editing\\'
        self.default_patches = self.home + '\\staging\\default_patches\\'
        self.repository_patches = self.home + '\\staging\\repository_patches\\'
        self.untextured_patches = self.home + '\\staging\\untextured_patches\\'

        self.stencil_metadata = self.home + '\\metadata\\stencils\\'
        self.template_metadata = self.home + '\\metadata\\templates\\'
        self.mappings_metadata = self.home + '\\metadata\\mappings\\'
        self.bindings_metadata = self.home + '\\metadata\\bindings\\'
        self.mappings_metadata_custom = self.home + '\\metadata\\mappings_custom\\'

        self.image_preprocess = self.home + '\\metadata\\preprocess.json'
        self.image_network = self.home + '\\metadata\\image_graph.json'
        self.binding_identifiers = self.home + '\\metadata\\binding_identifiers.json'

        self.output_path = self.home + '\\output\\synthesized_resources\\'

        web.download_minecraft(
            self.config['mc_version'], normpath(self.vanilla_pack))

        web.clone_repo(self.config['resource_pack'], self.resource_pack)

        web.clone_repo(self.config['key_repository'], self.key_repository)
        print('Sources installed')

        try:
            makedirs(self.home + '\\metadata')
        except FileExistsError:
            pass
