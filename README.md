# QGIS Processing Trajectory tools

This plugin adds trajectory tools to the QGIS Processing toolbox.

The core algorithms can also be used stand-alone, as demonstrated in the tests.


This plugin requires **GeoPandas**!

If you are on Windows, here's how to install GeoPandas for OSGeo4W:

1. OSGeo4W installer: install python3-pip
2. Environment variables: add GDAL_VERSION = 2.3.2 (or whichever version your OSGeo4W installation currently includes)
3. OSGeo4W shell: call C:\OSGeo4W64\bin\py3_env.bat
4. OSGeo4W shell: pip3 install geopandas (this will error at fiona)
5. From https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona: download Fiona-1.7.13-cp37-cp37m-win_amd64.whl
6. OSGeo4W shell: pip3 install <path-to-download>\Fiona-1.7.13-cp37-cp37m-win_amd64.whl
7. OSGeo4W shell: pip3 install geopandas

