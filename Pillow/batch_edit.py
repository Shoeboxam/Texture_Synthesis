import os
from PIL import Image


# Applies (filter/function) to all images in directory
def batch_apply(target, function, *args):
    def resize(tile, scalar):
        return tile.resize(tile.size*scalar)

    for root, folder, file in os.walk(target):
        current_image = Image.open(os.path.join(root, file))
        current_image = function(current_image, *args)
        current_image.save(os.path.join(root, file))
