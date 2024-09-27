# QGIS Processing Trajectools

The Trajectools plugin adds trajectory analysis algorithms to the QGIS Processing toolbox. 

![trajectools](https://github.com/movingpandas/qgis-processing-trajectory/assets/590385/218acb03-41be-4ea0-aee4-b773911d58f9)



## Requirements

Trajectools requires [MovingPandas](https://github.com/movingpandas/movingpandas) (a Python library for movement data analysis) and optionally integrates [scikit-mobility](https://scikit-mobility.github.io/scikit-mobility/) (for privacy tests), [stonesoup](https://stonesoup.readthedocs.io/) (for smoothing), and [gtfs_functions](https://github.com/Bondify/gtfs_functions) (for GTFS data support). 

### Conda install

The recommended way to install these dependencies is through conda/mamba:

```
(base) conda create -n qgis -c conda-forge python=3.9 
(base) conda activate qgis
(qgis) mamba install -c conda-forge qgis movingpandas scikit-mobility stonesoup
(qgis) pip install gtfs_functions
```

(More details: https://anitagraser.com/2023/01/21/pyqgis-jupyter-notebooks-on-windows-using-conda/)

### Pip install

If you cannot use conda, you may try installing from the QGIS Python Console:

```
import pip
pip.main(['install', 'movingpandas'])
pip.main(['install', 'scikit-mobility'])
pip.main(['install', 'stonesoup'])
pip.main(['install', 'gtfs_functions'])
```

## Plugin installation

The Trajectools plugin can be installed directly in QGIS using the built-in Plugin Manager:

![plugin manager](https://github.com/movingpandas/qgis-processing-trajectory/assets/590385/edd86ed3-8118-4163-bfe5-993b533e455c)

**Figure 1: QGIS Plugin Manager with Trajectools plugin installed.**

![image](https://github.com/user-attachments/assets/194ec6ed-2379-4572-b58b-a252d973f064)


**Figure 2: Trajectools (v2.3) algorithms in the QGIS Processing toolbox**

## Examples

The individual Trajectools algorithms are flexible and modular and can therefore be used on a wide array on input datasets, including, for example, the open [Microsoft Geolife dataset](http://research.microsoft.com/en-us/downloads/b16d359d-d164-469e-9fd4-daa38f2b2e13/) a [sample](https://github.com/emeralds-horizon/trajectools-qgis/tree/main/sample_data) of which is included in the plugin repo:

![image](https://github.com/movingpandas/qgis-processing-trajectory/assets/590385/3040ce90-552e-43a5-8660-17628f9b813a)

![Trajectools clipping screenshot](screenshots/trajectools2.PNG)

![image](https://github.com/user-attachments/assets/e3bbf2e5-e551-4f3e-bd29-8d19bdc33137)


## Citation information

![Zenodo badge](https://zenodo.org/badge/DOI/10.5281/zenodo.13847643.svg)

Please cite [0] when using Trajectools in your research and reference the appropriate release version using the Zenodo DOI.

[0] [Graser, A., & Dragaschnig, M. (2024, June). Trajectools Demo: Towards No-Code Solutions for Movement Data Analytics. In 2024 25th IEEE International Conference on Mobile Data Management (MDM) (pp. 235-238). IEEE.](https://ieeexplore.ieee.org/abstract/document/10591660)

```
@inproceedings{graser2024trajectools,
  title = {Trajectools Demo: Towards No-Code Solutions for Movement Data Analytics},
  author = {Graser, Anita and Dragaschnig, Melitta},
  booktitle = {2024 25th IEEE International Conference on Mobile Data Management (MDM)},
  pages = {235--238},
  year = {2024},
  organization = {IEEE},
  doi = {10.1109/MDM61037.2024.00048},
}
```
