#!/usr/bin/env python
 
from gimpfu import *
import os
import os.path
import sys

import array

home = os.path.expanduser('~\\.gimp-2.8\\mc_gui\\')

def gui_matchmaker():
  matches = []
  default = os.walk(home + 'templates\\defaults')
  replacer = os.walk(home + 'templates\\replacers')


  for filename_default, filename_replacer in zip(default, replacer):
    if (filename_default[2] != filename_replacer[2]):
      print("Mismatch")
    else:
      matches.append(filename_default[2])

  return matches

def image_to_pixel(image):
  drawable = pdb.gimp_image_get_active_layer(image)
  region = drawable.get_pixel_rgn(0, 0, image.width, image.height, 1, 1)
  pixels = array.array("B", region[0:image.width, 0:image.height])

  # p_size = len(region[0,0])
  # pixels = array.array("B", "\x00" * (image.width * image.width * p_size))
  return pixels


def gui_identify(index_pixel, index_template):
  return False

 
def gui_generator(glob_pattern, source):


  # Send errors and log to file
  sys.stderr = open(home + 'errorstream.txt', 'a')
  sys.stdout = open(home + 'outstream.txt', 'a')

  image_defaults = []
  image_replacers = []
  pixel_defaults = []
  pixel_replacers = []
  matches = gui_matchmaker()

  # Store templates in lists of pixel arrays
  for filename in matches:
    path = home + 'templates\\defaults\\' + filename[0]
    image = pdb.gimp_file_load(path, path)
    image_defaults.append(image)
    pixel_defaults.append(image_to_pixel(image))

    path = home + 'templates\\replacers\\' + filename[0]
    image = pdb.gimp_file_load(path, path)
    image_replacers.append(image)
    pixel_replacers.append(image_to_pixel(image))



  # Calculate scale increase
  path = home + 'templates\\defaults\\' + matches[0][0]
  width_default = pdb.gimp_file_load(path, path).width

  path = home + 'templates\\defaults\\' + matches[0][0]
  width_replacer = pdb.gimp_file_load(path, path).width

  resolution_scale = width_replacer / width_default


  # Retrieve paths to all default guis
  files = []
  for dirpath, dirnames, filenames in os.walk(source):
    for filename in [f for f in filenames if f.endswith(".png")]:
      files.append(os.path.join(dirpath, filename))

  # Loop through each default gui
  for path in files:

    image = pdb.gimp_file_load(path, path)
    image_export = pdb.gimp_image_new(image.width, image.height, 0)

    # Break image down into pixels
    pixels = image_to_pixel(image)

    # Loop through each pixel
    for index_pixel, pixel in enumerate(pixels):

      #  Check pixel against every template
      for index_template, base in enumerate(pixel_defaults):
        if (base[0] == pixel and gui_identify(index_pixel, index_template)):

          # Add matched element's corresponding replacer to export image
          inserted_element = pdb.gimp_image_insert_layer(image_export, image_replacers[index_template], 0, 0)

          # Convert array to cartesian coords
          x = index_pixel % image.height
          y = (index_pixel - x) / image.height

          pdb.gimp_layer_set_offsets(inserted_element, x * resolution_scale, y * resolution_scale)


    #pdb.gimp_file_save(image, drawable, path, path)
 
 
register(
  "plug-in-gui-generator",
  "GUI Generator",
  "Convert default GUIs to customizeable output",
  "Shoeboxam",
  "2014", #Copyright
  "2014/12/10",
  N_("MC GUI Conversion..."),
  "",
  [
    (PF_STRING, "glob_pattern", "Glob Pattern", "*.png"),
    (PF_STRING, "source", "Source Directory", "")
  ],
  [],
  gui_generator,
  menu="<Image>/Filters/Minecraft/",
  domain=("gimp20-python", gimp.locale_directory)
  )
 
main()