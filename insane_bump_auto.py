#!/usr/bin/env python

from gimpfu import *
import os

def mc_insanebump_auto(image, drawable, depth = 3, specular = 255): 
  path_suffixes = [ "_n", "_s", "_d", "_a", "_h", "_hn", "_ln", "_mn", "_sn" ]

  def modify_path(insertion):
    filename = image.filename
    index_insertion = filename.find(".png")
    return filename[:index_insertion] + insertion + filename[index_insertion:]

  resize_factor = 3

  #(image, drawable, new_width, new_height, new_image)
  pdb.plug_in_tile(image, drawable, image.width * resize_factor, image.height * resize_factor, False)

  #(item, flip_type, auto_center, axis)
  image = pdb.gimp_item_transform_flip_simple(image, 1, True, image.height / 2)

  #(image, drawable, remove_lighting, resizie, tile, new_width, edge_specular, def_specular, 
    #depth, large_details, medium_details, small_details, shape_recog, smoothstep, noise, invh, ao, prev)
  pdb.plug_in_insanebump(image, drawable, True, False, False, 1, specular != 255, specular, depth, 0, 0, 100, 0, False, False, False, 0, False)

  for suffix in path_suffixes[1 + specular!=255:]:
    os.remove(modify_path(suffix))

  map_normal_layer = pdb.gimp_file_load_layer(image, modify_path(path_suffixes[0]))

  image = pdb.gimp_item_transform_flip_simple(map_normal_layer, 1, True, image.height / 2)

  #(image, new_width, new_height, offx, offy)
  pdb.gimp_image_crop(image, image.width / resize_factor, image.height / resize_factor, (image.width - (image.width / resize_factor)) / 2, (image.height - (image.height / resize_factor)) / 2)



register(
  "python_fu_normalmap_autogen",
  "InsaneBump Autorun",
  "Convert texture tile to normal map using InsaneBump",
  "Alias: Shoeboxam",
  "Copyright Shoeboxam 2014",
  "2014/12/10",
  N_("InsaneBump Auto..."),
  "*",
  [
    (PF_INT, "depth", "Depth", 3),
    (PF_INT, "specular", "Specular", 255)
  ],
  [],
  mc_insanebump_auto,
  menu="<Image>/Filters/Map/",
  domain=("gimp20-python", gimp.locale_directory)
  )

main()