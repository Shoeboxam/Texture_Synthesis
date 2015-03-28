from Raster import Raster
from image_filters import *

img = Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
img = colorize(img, 1., .6, .3, .01)
PIL = img.get_image()

PIL.show()
