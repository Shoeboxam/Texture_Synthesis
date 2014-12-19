#!/usr/bin/env python
 
from gimpfu import *
import os
import os.path
import sys

import array
 
def gui_generator(glob_pattern, source, export):

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

    success = False

    # Break image down into pixels
    pixel_array = image_to_pixel(image)

    # Loop through each pixel
    for pixel_index, pixel in enumerate(pixel_array):

      # Check pixel against every template
      for template_index, template_pixel_array in enumerate(pixel_defaults):

        def gui_identify(offset_x, offset_y, template_index):
          template_width = image_defaults[template_index].width
          template_height = image_defaults[template_index].height

          # Ensure match can fit
          if (template_width + offset_x > image.width or template_height + offset_y > image.height): 
            return False

          # Check template against image at offset
          for template_pixel_index, template_pixel in enumerate(template_pixel_array):
            template_pixel_x = template_pixel_index % template_width
            template_pixel_y = (template_pixel_index - template_pixel_x) / template_height

            if (template_pixel != pixel_array[pixel_index + template_pixel_x + (template_pixel_y * image.width)]):
              return False

          #Every pixel in template matched, therefore template has been identified in source image
          return True

        # Convert array index to cartesian coordinates
        x = pixel_index % image.height
        y = (pixel_index - x) / image.height

        if (gui_identify(x, y, template_index)):

          # Add matched element's corresponding replacer to export image
          replacer_insert = pdb.gimp_layer_new_from_drawable(pdb.gimp_image_get_active_layer(image_replacers[template_index]), image_export)
          print(type(replacer_insert))
          # pdb.gimp_image_insert_layer(image_export, replacer_insert, pdb.gimp_image_get_active_layer(image_export), 0)

          # Move inserted element to location of match
          pdb.gimp_layer_set_offsets(replacer_insert, x * resolution_scale, y * resolution_scale)

    if success:
      path_export = path.replace(source, export, 1)
      pdb.gimp_file_save(image_export, pdb.gimp_image_merge_visible_layers(image_export, 1), path_export, path_export)
 
 
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
    (PF_STRING, "source", "Source Directory", ""),
    (PF_STRING, "export", "Export Directory", "")
  ],
  [],
  gui_generator,
  menu="<Image>/Filters/Minecraft/",
  domain=("gimp20-python", gimp.locale_directory)
  )
 
main()