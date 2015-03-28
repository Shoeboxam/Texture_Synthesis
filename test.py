from Raster import Raster
from image_filters import *

img = Raster.from_path(r"C:\Users\mike_000\Desktop\pack.png")
print(img.alpha)
img.to_hsv()
print(img.pixels)
img.to_rgb()
print(img.pixels)

PIL = img.get_image()

PIL.show()
