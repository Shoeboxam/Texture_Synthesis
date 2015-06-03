Texture Synthesis
=================


Procedural sprite generation to automate Minecraft resource pack mod support.  

Detects and classifies patterns in the default resource pack. Distinctive patterns are tied to templates. 
Every default image classified with a template is profiled, and the data is stored in a tree of json files.

The process of profiling decomposes each template into spectral clusters, or zones of discrete information. 
Predominant colors, data variance and lightness are then calculated from each of the component clusters of every image. 
This data taken in profiling is used to mould custom graphic templates into completed graphics.

This project has support for converting between Github repository format (mod patches) and resource pack format (whole), 
and can read mods and resourcepacks directly from a Minecraft instance.


Structure
---------
Raster: custom image object, filters and analysis tools  
Utilities: implementation of Minecraft use case  
Specializations: scripts for generating specific classes of textures


TODO
---------
Call specialization scripts from main  
Multithread profiling/skeleton generation  
Add support for gui generation within specialization section  
Fuzzy cluster matching and ignore logic  
Scrape MCF Modlist to automatically compile mod directory  
Clean up paths/add config system  

