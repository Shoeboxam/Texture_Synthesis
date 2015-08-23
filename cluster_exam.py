from Raster import filters, Raster
from Synthesizer.metadata import analyze_image
import json
from ast import literal_eval
import numpy as np

apple = Raster.Raster.from_path(
    r"C:\Users\mike_000\Synthesizer\sources\resource_pack\assets\minecraft\textures\blocks\flower_tulip_pink.png")
print(apple.name)
print(apple.shape)

apple_metadata = json.loads(open(r"C:\Users\mike_000\Synthesizer\metadata\templates\apple.png.json").read())

cluster_map = np.array(literal_eval(apple_metadata['cluster_map']))
print(cluster_map.reshape(apple.shape))

layers = filters.layer_decomposite(apple, cluster_map)

for id, layer in enumerate(layers):
    layer.get_image().save(r"C:\Users\mike_000\Desktop\\" + layer.name + '_' + str(id) + ".png")

print(analyze_image(layers[1]))
