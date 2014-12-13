#!/usr/bin/env python

from gimpfu import *
import os

def normalmap_wrapper(glob_pattern, source):
  glob = pdb.file_glob(source + os.sep + glob_pattern, 1)

  for path in glob[1]:
    image = pdb.gimp_file_load(path)
    drawable = pdb.gimp_image_get_active_layer(image)
    pdb.plug_in_normalmap(image, drawable, 0, .04, 6, 1, 0, 1, 0, 0, 0, 1, 0, 0, drawable)
    pdb.gimp_file_save(image, drawable, path, path)


register(
  "plug-in-normalmap-wrapper",
  "Normalmap Autorun",
  "Convert texture tile to normal map using Normalmap plugin",
  "Alias: Shoeboxam",
  "Shoeboxam 2014", #Copyright
  "2014/12/10",
  N_("Normalmap Auto..."),
  "",
  [
    (PF_STRING, "glob_pattern", "Glob Pattern", "*.*"),
    (PF_DIRNAME, "source_directory", "Source Directory", "")
  ],
  [],
  normalmap_wrapper,
  menu="<Image>/Filters/Map/",
  domain=("gimp20-python", gimp.locale_directory)
  )

main()

#pdb.plug_in_normalmap(image, drawable, 0, .04, 6, 1, 0, 1, 0, 0, 0, 1, 0, 0, drawable)