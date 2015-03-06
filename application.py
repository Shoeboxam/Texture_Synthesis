from make_default import *
from file_diff import *

home = os.path.normpath("C:\\Users\mike_000\AppData\Roaming\.ftb\FTBInfinity\minecraft")
default_pack = os.path.normpath('C:\\Users\mike_000\AppData\Roaming\.ftb\FTBInfinity\minecraft\\resourcepacks\default\\')
key_repository = os.path.normpath('C:\\Users\mike_000\Textures\Modded-1.7.x')

# Default pack
shutil.rmtree(home + "\\resourcepacks\\temp\\", True)

make_default(home)
remove_cruft(home + "\\resourcepacks\\temp\\")
extract_matches(home + "\\resourcepacks\\temp\\", home + "\\resourcepacks\\default\\", key_repository)

shutil.rmtree(home + "\\resourcepacks\\temp\\", True)


# Diff pack
diff_pack = default_pack.replace("resourcepacks\default", "resourcepacks\default_diff")
untextured_paths = untextured_paths(default_pack, key_repository)

copytree_wrapper(default_pack, diff_pack, untextured_paths)

# Remove extra files and folders from diff using make_default.py
remove_cruft(diff_pack)
