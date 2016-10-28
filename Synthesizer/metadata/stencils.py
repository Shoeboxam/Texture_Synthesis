import json
import os

from Raster.Raster import Raster


def make_stencil(stencil_name, quantity, stencil_staging, stencil_configs, colorize, relative_path):

    masks = []

    for id in range(quantity):
        stencil_path = os.path.normpath(stencil_staging + "\\" + stencil_name + "_" + str(id+1) + ".png")
        stencil = Raster.from_path(stencil_path, 'RGBA')
        masks.append(stencil.mask.tolist())

    stencil_path = stencil_staging + "\\" + stencil_name + "_1.png"
    stencil_data = dict(name=stencil_name,
                        shape=Raster.from_path(stencil_path, 'RGBA').shape.tolist(),
                        mask=masks,
                        colorize=colorize,
                        path=relative_path)

    with open(stencil_configs + '//' + stencil_name + ".json", 'w') as output_file:
        json.dump(stencil_data, output_file, sort_keys=True)
