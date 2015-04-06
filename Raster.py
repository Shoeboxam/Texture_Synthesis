import numpy as np
from PIL import Image
import colorsys


class Raster:

    def __init__(self, pixels, width, height, mode, channels, bits=8, alpha=False):

        pixels = np.array(pixels)

        # Split pixel data's mask away from color information
        self.colors = pixels[:, :channels - alpha]
        self.mask = None
        if alpha:
            self.mask = pixels[:, channels - 1]
        self.width = width
        self.height = height
        self.mode = mode
        self.channels = channels
        self.bits = bits
        self.alpha = alpha

    @classmethod
    def from_image(self, image):
        bit_depth = {'1': 1, 'L': 8, 'P': 8, 'RGB': 8, 'RGBA': 8, 'CMYK': 8, 'YCbCr': 8, 'I': 32, 'F': 32}
        channel_depth = {'1': 1, 'L': 1, 'P': 1, 'RGB': 3, 'RGBA': 4, 'CMYK': 4, 'YCbCr': 3, 'I': 1, 'F': 1}

        width, height = image.size

        mode = image.mode
        channels = channel_depth[image.mode]

        alpha = False
        if mode.endswith('A'):
            alpha = True
            mode = mode.replace('A', '')

        bits = bit_depth[image.mode]
        pixels = np.asarray(image).reshape(width * height, channels).astype(float) / (2**bits - 1)

        return self(pixels, width, height, mode, channels, bits, alpha)

    @classmethod
    def from_path(self, path):
        return self.from_image(Image.open(path))

    @classmethod
    def from_array(self, array, mode='RGB'):

        array = np.array(array)
        # No normalization
        width, height, channels = array.shape
        # channels = len(array[0, 0])
        pixels = np.reshape(array, (width * height, channels)).astype(float)
        alpha = False
        if channels == 4:
            mode += 'A'
            alpha = True
        return self(pixels, width, height, mode, channels, alpha=alpha)

    # Combines alpha channel with color
    def with_alpha(self):
        mask = None
        if self.alpha:
            mask = np.reshape(self.mask, (self.mask.shape[0], 1))
        else:
            mask = np.ones((self.width * self.height))
        return np.append(self.colors, mask, axis=1)

    def get_image(self):
        self.to_rgb()

        mode = self.mode
        pixels = self.colors

        if self.alpha:
            mode += 'A'
            pixels = self.with_alpha()

        pixels = np.reshape(pixels, (self.width, self.height, self.channels))

        return Image.fromarray(np.ceil(pixels * (2**self.bits - 1)).astype(np.uint8), mode=mode)

    def get_opaque(self, threshold=0):
        solid = []
        for color, alpha in zip(self.colors, self.mask):
            if alpha != 0:
                solid.append(color)
        return solid

    def channel(self, identifier):
        column = self.mode.index(identifier)
        return self.colors[:, column]

    def to_hsv(self):
        if 'RGB' in self.mode:
            for index, (r, g, b) in enumerate(self.colors):
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                self.colors[index] = [h, s, v]
                self.mode = 'HSV'

    def to_rgb(self):
        if 'HSV' in self.mode:
            for index, (h, s, v) in enumerate(self.colors):
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                self.colors[index] = [r, g, b]
                self.mode = 'RGB'

    # Optional fragment-based manipulation
    def filter(self, func, *args):
        for index, (a, b, c) in enumerate(self.colors):
            self.colors[index] = func((a, b, c), *args)
