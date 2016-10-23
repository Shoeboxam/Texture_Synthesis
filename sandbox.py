from Raster.Raster import Raster
import numpy as np
image = Raster.from_path(r"C:\Users\mike_000\Desktop\images.png", "RGBA")

image_edited = Raster.from_array(np.rot90(image.get_tiered()), "RGBA")


shape = image.get_tiered().shape[:2]
print(shape)
coords = np.zeros(shape + (2,))
for indice_x in range(shape[0]):
    for indice_y in range(shape[1]):
        coords[indice_x, indice_y, 0] = indice_x
        coords[indice_x, indice_y, 1] = indice_y

x_transposed = coords[:,:,0].T
y_transposed = coords[:,:,1].T
image_rotated = np.zeros(tuple(reversed(shape)) + (4,))
print(image_rotated.shape)
for indice_x in range(shape[1]):
    for indice_y in range(shape[0]):
        image_rotated[indice_x, indice_y] = image.get_tiered()[x_transposed[indice_x,indice_y], y_transposed[indice_x, indice_y]]
print(image_rotated)
Raster.from_array(image_rotated, "RGBA").save(r"C:\Users\mike_000\Desktop\image_rotated.png")
