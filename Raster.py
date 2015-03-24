import numpy as np
from PIL import Image
import colorsys


class Raster:

    def __init__(self, pixels, width, height, color_model):
        self.pixels = pixels
        self.width = width
        self.height = height
        self.model = color_model

    def from_image(self, image):
        self.width, self.height = image.size
        self.pixels = np.asarray(image).reshape(self.width * self.height, 4).astype(float) / 2**image.bits

    def from_path(self, path):
        self.from_image(Image.open(path))

    def get_image(self):
        pixels = np.reshape(self.pixels.astype(np.uint8), (self.width, self.height, 4))
        return Image.fromarray(np.ceil(pixels * 255), mode='RGBA')

    def get_opaque(self, threshold = 0):
        return self.pixels[self.pixels[3]>threshold]

    def to_hsv(self):
        if self.model == 'rgb':
            for index, (r, g, b, a) in enumerate(self.pixels):
                self.pixels[index] = [*colorsys.rgb_to_hsv(r, g, b), a]

    def to_rgb(self):
        if self.model == 'hsv':
            for index, (h, s, v, a) in enumerate(self.pixels):
                self.pixels[index] = [*colorsys.hsv_to_rgb(h, s, v), a]