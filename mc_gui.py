#!/usr/bin/env python
 
from gimpfu import *
import os
import os.path
import sys

import array
 
def normalmap_wrapper(glob_pattern, source):


  # Send errors and log to file
  sys.stderr = open(os.path.expanduser('~\Desktop\errorstream.txt'), 'a')
  sys.stdout = open(os.path.expanduser('~\Desktop\outstream.txt'), 'a')

  # Get all the files from the directory
  files = []
  for dirpath, dirnames, filenames in os.walk(source):
      for filename in [f for f in filenames if f.endswith(".png")]:
          files.append(os.path.join(dirpath, filename))

  # Loop through each file
  for path in files:
    # Debug
    print(path)
    # Load the file
    image = pdb.gimp_file_load(path, path)

    drawable = pdb.gimp_image_get_active_layer(image)
    drawable_export = drawable

    region = drawable.get_pixel_rgn(0, 0, image.width, image.height, 1, 1)
    region_export = region

    pixels = array.array("B", region[0:image.width, 0:image.height])

    p_size = len(region[0,0])
    pixels = array.array("B", "\x00" * (image.width * image.width * p_size))
    pixels_export = pixels

    for index, value in enumerate(pixels):
      print(value)

    #pdb.gimp_file_save(image, drawable, path, path)
 
 
register(
  "plug-in-gui-generator",
  "GUI Generator",
  "Convert default GUIs to customizeable output",
  "Shoeboxam",
  "2014", #Copyright
  "2014/12/10",
  N_("Normalmap Auto..."),
  "",
  [
    (PF_STRING, "glob_pattern", "Glob Pattern", "*.png"),
    (PF_STRING, "source", "Source Directory", "")
  ],
  [],
  normalmap_wrapper,
  menu="<Image>/Filters/Map/",
  domain=("gimp20-python", gimp.locale_directory)
  )
 
main()