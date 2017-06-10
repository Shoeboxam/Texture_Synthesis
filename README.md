Texture Synthesis
=================


Procedural sprite generation with an application in Minecraft resource pack mod support. 
Core image manipulation logic, from filters, to the data structure, are all handled in the raster submodule.

The Minecraft application creates an undirected graph from groups of related images. The most connected nodes within each bunch are designated as templates. 
Every default image classified with a template is profiled, and the data is stored in a tree of json files.

The process of profiling decomposes each template into spectral clusters, or zones of discrete information. 
Predominant colors, data variance and lightness are then calculated from each of the component clusters of every image. 
This data taken in profiling is used to transform existing resource pack images into new graphics. From a bird's eye view, a resource pack's incomplete implementation of the default graphic tree is filled-in using correlations, graphic analysis and custom filters.

This project has support for converting between Github repository format (mod patches) and resource pack format (whole), 
and can read mods and resourcepacks directly from a Minecraft instance.


Structure
---------
Raster: custom image object, filters and analysis tools  
Synthesizer: implementation of Minecraft use case  
Interface: manual config editing to create initial training data


TODO
---------
Fuzzy cluster matching and ignore logic  
Scrape MCF Modlist to automatically compile mod directory  

