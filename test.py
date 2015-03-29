from Raster import Raster
from Filters import *
from color_utilities import *

img = Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
img = colorize(img, .8, .5, .2, .3, .01, 0)
PIL = img.get_image()

# Tester
print(mean_hue((.23, .51, .98)))

PIL.show()
