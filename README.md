Texture Synthesis
=================


Collection of scripts to generate sprites for Soartex mod support.


1. Unzip all mod zips
2. Rename mod directory with name of assets folder
3. Pair asset folder with mod name
4. Rename mod folders to repository names
5. Duplicate all files in default pack that are not in resource pack
6. Detect textures that are derivatives of template files (Pearson correlation)
7. Analyze detected textures (KMeans clustering)
8. Save shape, representative colors and light point to json files
9. Decompose resource templates into layers (lightness based alpha masking)
10. Sort json colors, then filter decomposed image to match
11. Recomposite layers with simplified additive alpha blending
12. Adjust contrast and lightness to match mod sprite
13. Save image result to output directory tree

Dependencies
---------------

[Pillow](https://pillow.readthedocs.org/): image loading and saving
[Numpy](http://www.numpy.org): numerical arrays for image processing
[Scikit-Learn](http://scikit-learn.org/stable/): image detection and analysis
[Matplotlib](http://matplotlib.org): unit testing
