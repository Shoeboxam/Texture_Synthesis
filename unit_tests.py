from Raster import Raster, analyze
from Raster.math_utilities import *


def test_math():
    # Check the modular math with specific problem points
    assert(circular_mean((.75, .25)) == .5)
    assert(round(circular_mean((.8, .1), (1, 2)), 1) == 0)
    assert(circular_mean((.2, .8)) == 0)
    assert(circular_mean((.1, .4)) == np.mean((.1, .4)))
    assert(circular_mean((2.7, -.7)) == 0.5)
    assert(circular_mean((50.9, 50.1, .5)) == 0)

    # Ensure sorting logic works
    assert(circular_sort((0.23, .153, .8423)) == [0.8423, 0.153, 0.23])


def test_raster_analyze():
    # Simple image construction
    test_image = Raster.Raster([[1., 1., 1.], [0., 0., 0.]], (2, 1), 'RGBA', mask=[1., 0.2])

    # Ensure alpha is weighted in calculations
    # NOTE: implicitly and permanently casts raster into HSV
    assert(analyze.mean(test_image, 'V') > .5)

    # 1 == 1
    assert(analyze.correlate(test_image, test_image) == 1.)

    # Change color space back
    test_image.to_rgb()

    # Test color extraction with known expected values
    assert(sum(np.array(analyze.color_extract(test_image, 2)).flatten()) == 3.)
    assert(sum(np.array(analyze.color_extract(test_image, 1)).flatten()) == 1.5)
