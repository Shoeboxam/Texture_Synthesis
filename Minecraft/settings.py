from os.path import normpath
from os.path import expanduser

# .minecraft directory
home = normpath(expanduser(r"~\AppData\Roaming\.ftb\FTBInfinity\minecraft\\"))

default_pack = normpath(home + '\\resourcepacks\default\\')
diff_pack = normpath(home + '\\resourcepacks\default_diff\\')
resource_pack = normpath(expanduser(r'~\Textures\Invictus\Modded-1.7.x'))
metadata_pack = normpath(home + '\\resourcepacks\default_metadata\\')

mods_directory = normpath(home + '\\mods\\')
key_repository = normpath(expanduser(r'~\Textures\Modded-1.7.x'))
template_path = normpath(home + r'\resourcepacks\templates')

output_path = normpath(home + r'\resourcepacks\synthesized_resources\\')
