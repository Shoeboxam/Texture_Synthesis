#!/usr/bin/env python
 
from gimpfu import *
import os
import os.path
import glob 
import sys
 
# This adds the suffix to the end of the file
def modify_path(image, insertion):
  filename = image.filename
  index_insertion = filename.find(".png")
  return filename[:index_insertion] + insertion + filename[index_insertion:]
 
# This does all the work
def normalmap_wrapper(glob_pattern, source, depth):

  path_suffixes = [ "_n", "_s", "_d", "_a", "_h", "_hn", "_ln", "_mn", "_sn" ]


  # Send errors and log to file
  sys.stderr = open(os.path.expanduser('~\Desktop\errorstream.txt'), 'a')
  sys.stdout = open(os.path.expanduser('~\Desktop\outstream.txt'), 'a')
  # Get all the files from the directory
  #glob1 = glob.glob(source + glob_pattern)
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

    resize_factor = 3

    # Tile to fix interpolation of edge pixels
    pdb.plug_in_tile(image, drawable, image.width * resize_factor, image.height * resize_factor, False)

    # Vertical flip to invert light cast
    image = pdb.gimp_image_flip(image, 1)

    #(image, drawable, remove_lighting, resizie, tile, new_width, edge_specular, def_specular, 
      #depth, large_details, medium_details, small_details, shape_recog, smoothstep, noise, invh, ao, prev)
    pdb.plug_in_insanebump(image, drawable, True, False, False, 1, 0, 255, depth, 0, 0, 100, 0, False, False, False, 0, False)

    for suffix in path_suffixes[1:]:
      os.remove(modify_path(suffix))

    map_normal_layer = pdb.gimp_file_load_layer(image, modify_path(path_suffixes[0]))

    # Unflip!
    image = pdb.gimp_image_flip(image, 1)

    # Untile!
    pdb.gimp_image_crop(image, image.width / resize_factor, image.height / resize_factor, (image.width - (image.width / resize_factor)) / 2, (image.height - (image.height / resize_factor)) / 2)


    # Alternative normal script plugin
    #pdb.plug_in_normalmap(image, drawable, 0, .04, 6, 1, 0, 1, 0, 0, 0, 1, 0, 0, drawable)


    # Change to new file name
    path_n = modify_path(image, '_n')
    # Export
    pdb.gimp_file_save(image, drawable, path_n, path_n)
 
 
register(
  "plug-in-normalmap-wrapper",
  "Normalmap Autorun",
  "Convert texture tile to normal map using Normalmap plugin",
  "Shoeboxam and Goldbattle",
  "2014", #Copyright
  "2014/12/10",
  N_("Normalmap Auto..."),
  "",
  [
    (PF_STRING, "glob_pattern", "Glob Pattern", "*.png"),
    (PF_STRING, "source", "Source Directory", ""),
    (PF_INT, "depth", "Depth", 3)
  ],
  [],
  normalmap_wrapper,
  menu="<Image>/Filters/Map/",
  domain=("gimp20-python", gimp.locale_directory)
  )
 
main()
 
#pdb.plug_in_normalmap(image, drawable, 0, .04, 6, 1, 0, 1, 0, 0, 0, 1, 0, 0, drawable)
# (plug-in-normalmap-wrapper 0 "*.png" "G:\\Patrick\\Downloads\\blocks\\")