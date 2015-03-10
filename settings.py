import os

# .minecraft directory
home = os.path.normpath("C:\\Users\mike_000\AppData\Roaming\.ftb\FTBInfinity\minecraft")
default_pack = os.path.normpath('C:\\Users\mike_000\AppData\Roaming\.ftb\FTBInfinity\minecraft\\resourcepacks\default\\')
diff_pack = default_pack.replace("resourcepacks\default", "resourcepacks\default_diff")
resource_pack = os.path.normpath('C:\\Users\mike_000\Textures\Invictus\Modded-1.7.x')
key_repository = os.path.normpath('C:\\Users\mike_000\Textures\Modded-1.7.x')
minecraft_jar = os.path.normpath('C:\\Users\mike_000\AppData\Roaming\.ftb\\versions\1.7.10')
template_path = os.path.normpath(r'C:\\Users\mike_000\AppData\Roaming\.ftb\FTBInfinity\minecraft\resourcepacks\templates')