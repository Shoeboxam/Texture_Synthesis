import numpy as np
from PIL import Image
import colorsys


class Raster:

    def __init__(self, pixels, width, height, mode, channels, bits=8, alpha=False):
        # Split pixel data's mask away from color information
        
        self.pixels = pixels[:, :channels - alpha]
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
        if mode == 'RGBA':
            alpha = True
            mode = 'RGB'

        bits = bit_depth[image.mode]
        pixels = np.asarray(image).reshape(width * height, channels).astype(float) / (2**bits - 1)

        return self(pixels, width, height, mode, channels, bits, alpha)

    @classmethod
    def from_path(self, path):
        return self.from_image(Image.open(path))

    def get_image(self):
        self.to_rgb()

        mode = self.mode
        pixels = self.pixels

        if self.alpha:
            mode += 'A'

            mask = np.reshape(self.mask, (self.mask.shape[0], 1))
            pixels = np.append(self.pixels, mask, axis=1)

        pixels = np.reshape(pixels, (self.width, self.height, self.channels))

        return Image.fromarray(np.ceil(pixels * (2**self.bits - 1)).astype(np.uint8), mode=mode)

    def get_opaque(self, threshold=0):
        return self.pixels[self.pixels[3] > threshold]

    def to_hsv(self):
        if self.mode == 'RGB':
            for index, (r, g, b) in enumerate(self.pixels):
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                self.pixels[index] = [h, s, v]
                self.mode = 'HSV'

    def to_rgb(self):
        if self.mode == 'HSV':
            for index, (h, s, v) in enumerate(self.pixels):
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                self.pixels[index] = [r, g, b]
                self.mode = 'RGB'
