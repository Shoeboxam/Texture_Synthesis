Texture Synthesis
=================


Procedural sprite generation for Soartex mod support through Python.


1. Unzip all mod zips
2. Rename mod directory with name of assets folder
3. Pair asset folder with mod name
4. Rename mod folders to repository names
5. Extract all files in default pack that are not in resource pack
6. Detect repetitive image patterns and identify as templates
7. Detect textures that are derivatives of template files (Pearson correlation)
8. Analyze detected textures (KMeans with color coordinates)
9. Save shape, representative colors, lightness, contrast to json files
10. Adjust contrast and lightness to match mod sprite
11. Decompose resource templates into layers (alpha masking or spatial clustering)
12. Sort json colors, then filter image components to match
13. Recomposite layers with simplified additive alpha blending
14. Mask saturation in lighter values
15. Save image result to output directory tree


TODO
---------------

- Spatial clustering in decomposure and analysis  
- Automatically create templates  
- Reduce sat in lighter values  
- General code cleanup/documentation  


Dependencies
---------------

[Pillow](https://pillow.readthedocs.org/): image loading and saving  
[Numpy](http://www.numpy.org): numerical arrays for image processing  
[Scikit-Learn](http://scikit-learn.org/stable/): image detection and analysis  
[Matplotlib](http://matplotlib.org): unit testing  
