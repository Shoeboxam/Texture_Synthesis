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
def normalmap_wrapper(glob_pattern, source):
  # Send errors and log to file
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


    # Call the normal script plugin
    pdb.plug_in_normalmap(image, drawable, 0, .04, 6, 1, 0, 1, 0, 0, 0, 1, 0, 0, drawable)


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
    (PF_STRING, "source", "Source Directory", "")
  ],
  [],
  normalmap_wrapper,
  menu="<Image>/Filters/Map/",
  domain=("gimp20-python", gimp.locale_directory)
  )
 
main()
 
#pdb.plug_in_normalmap(image, drawable, 0, .04, 6, 1, 0, 1, 0, 0, 0, 1, 0, 0, drawable)
# (plug-in-normalmap-wrapper 0 "*.png" "G:\\Patrick\\Downloads\\blocks\\")