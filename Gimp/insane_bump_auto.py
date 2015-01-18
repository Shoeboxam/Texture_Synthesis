#!/usr/bin/env python

from gimpfu import *
import os

def mc_insanebump_auto(image, drawable, depth = 3.0, specular = 255): 
  path_suffixes = [ "_n", "_s", "_d", "_a", "_h", "_hn", "_ln", "_mn", "_sn" ]

  def modify_path(insertion):
    filename = image.filename
    index_insertion = filename.find(".png")
    return filename[:index_insertion] + insertion + filename[index_insertion:]

  resize_factor = 3

  #(image, drawable, new_width, new_height, new_image)
  pdb.plug_in_tile(image, drawable, image.width * resize_factor, image.height * resize_factor, False)

  #(item, flip_type, auto_center, axis)
  pdb.gimp_image_flip(image, 1)

  pdb.gimp_displays_flush()

  pdb.gimp_message(type(drawable))


  try:
    (image, drawable, remove_lighting, resizie, tile, new_width, edge_specular, def_specular, 
      #depth, large_details, medium_details, small_details, shape_recog, smoothstep, noise, invh, ao, prev)
    pdb.plug_in_insanebump(image, drawable, 1, 0, 0, 1, 0, specular, depth, 1, 1, 100, 0, 0, 0, 0, 0, 0)
  except RuntimeError:
    pdb.gimp_message("RuntimeError: Call didn't work!")

  for suffix in path_suffixes[1 + specular!=255:]:
    os.remove(modify_path(suffix))

  map_normal_layer = pdb.gimp_file_load_layer(image, modify_path(path_suffixes[0])) 

  image = pdb.gimp_item_transform_flip_simple(map_normal_layer, 1, True, image.height / 2)

  #(image, new_width, new_height, offx, offy)
  pdb.gimp_image_crop(image, image.width / resize_factor, image.height / resize_factor, (image.width - (image.width / resize_factor)) / 2, (image.height - (image.height / resize_factor)) / 2)



register(
  "plug-in-insanebump-auto",
  "InsaneBump Autorun",
  "Convert texture tile to normal map using InsaneBump",
  "Alias: Shoeboxam",
  "Shoeboxam 2014", #Copyright
  "2014/12/10",
  N_("InsaneBump Auto..."),
  "*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_FLOAT, "depth", "Depth", 3.0),
    (PF_INT, "specular", "Specular", 255)
  ],
  [],
  mc_insanebump_auto,
  menu="<Image>/Filters/Map/",
  domain=("gimp20-python", gimp.locale_directory)
  )

main()

#pdb.plug_in_normalmap(image, drawable, 0, .04, 6, 1, 0, 1, 0, 0, 0, 1, 0, 0, drawable)