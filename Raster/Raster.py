import numpy as np
from PIL import Image
import colorsys


class Raster:

    def __init__(self, colors, shape, mode, mask=None):

        self.shape = shape
        self.colors = colors
        self.mask = mask
        self.mode = mode

    @property
    def colors(self):
        return self.colors

    @colors.setter
    def colors(self, colors):
        colors = np.array(colors).astype(np.float64)

        if len(colors) != np.product(self.shape):
            raise ValueError("Length of colors does not match shape")

        if np.max(colors) > 1 or np.min(colors) < 0:
            raise ValueError("Color elements must be between zero and one")
        self.colors = colors

    @property
    def mask(self):
        return self.mask

    @mask.setter
    def mask(self, mask):
        if mask is None:
            mask = np.ones(np.product(self.shape))

        mask = np.array(mask).astype(np.float64)
        if len(mask) != np.product(self.shape):
            raise ValueError("Mask must have same number of elements as colors")

        if np.max(mask) > 1 or np.min(mask) < 0:
            raise ValueError("Mask elements must be between zero and one")
        self.mask = np.array(mask).astype(np.float64)

    @property
    def mode(self):
        return self.mode

    @mode.setter
    def mode(self, mode):
        channel_depth = {'1': 1, 'L': 1, 'P': 1, 'RGB': 3, 'RGBA': 4, 'CMYK': 4, 'YCbCr': 3, 'I': 1, 'F': 1}
        if mode not in channel_depth.keys():
            raise ValueError("Mode is not recognized")
        if channel_depth[mode] != self.colors.shape[1]:
            raise ValueError("Color mode incompatible with number of channels given")

    @classmethod
    def from_image(cls, image, mode=None):
        bit_depth = {'1': 1, 'L': 8, 'P': 8, 'RGB': 8, 'RGBA': 8, 'CMYK': 8, 'YCbCr': 8, 'I': 32, 'F': 32}
        channel_depth = {'1': 1, 'L': 1, 'P': 1, 'RGB': 3, 'RGBA': 4, 'CMYK': 4, 'YCbCr': 3, 'I': 1, 'F': 1}

        if mode is not None:
            image = image.convert(mode)

        # Convert to flat numpy array
        channels = channel_depth[mode]
        width, height = image.size
        pixels = np.asarray(image).reshape(width * height, channels)

        # Normalize data
        bits = bit_depth[image.mode]
        pixels = pixels.astype(np.float64) / (2**bits - 1)

        # Separate mask
        colors = pixels[:, :channels-1]
        mask = pixels[:, channels-1]

        return cls(colors, image.size, image.mode.replace('A', ''), mask)

    @classmethod
    def from_path(cls, path, mode):
        return cls.from_image(Image.open(path), mode)

    # Combines alpha channel with color
    def with_alpha(self):
        mask = np.reshape(self.mask, (len(self.mask), 1))
        return np.append(self.colors, mask, axis=1)

    def get_image(self):
        self.to_rgb()
        pixels = np.reshape(self.with_alpha(), (self.shape[0], self.shape[1], 4))
        return Image.fromarray(np.ceil((pixels * 255).astype(np.uint8)), mode=self.mode)

    def get_opaque(self):
        solid = []
        for color, alpha in zip(self.colors, self.mask):
            if alpha != 0:
                solid.append(color)
        return np.array(solid)

    def channel(self, identifier, opaque=False):
        if opaque:
            colors = self.get_opaque()
        else:
            colors = self.colors

        # REMINDER: Only works for HSV/RGB switching
        if identifier not in self.mode:
            if self.mode == 'RGB':
                self.to_hsv()
            else:
                self.to_rgb()

        column = self.mode.index(identifier)
        return colors[:, column]

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
