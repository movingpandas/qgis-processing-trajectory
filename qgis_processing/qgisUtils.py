# -*- coding: utf-8 -*-

"""
***************************************************************************
    qgisUtils.py
    ---------------------
    Date                 : December 2018
    Copyright            : (C) 2018 by Anita Graser
    Email                : anitagraser@gmx.at
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import sys 
import pandas as pd
from geopandas import GeoDataFrame
from PyQt5 import QtCore
from shapely.geometry import Point
from datetime import datetime
from pyproj import CRS

sys.path.append("..")

from processing_trajectory.trajectory import Trajectory


def trajectories_from_qgis_point_layer(layer, time_field_name, trajectory_id_field, time_format):
    names = [field.name() for field in layer.fields()]
    data = []
    for feature in layer.getFeatures():
        my_dict = {}
        for i, a in enumerate(feature.attributes()):
            if names[i] == time_field_name:
                if type(a) == QtCore.QDateTime:
                    my_dict[names[i]] = a.toPyDateTime()
                else:
                    my_dict[names[i]] = datetime.strptime(a, time_format)
            else:
                my_dict[names[i]] = a
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        my_dict['geometry'] = Point((x, y))
        data.append(my_dict)
    df = pd.DataFrame(data).set_index(time_field_name)
    crs = CRS(int(layer.sourceCrs().geographicCrsAuthId().split(':')[1]))
    geo_df = GeoDataFrame(df, crs=crs)
    df_by_id = dict(tuple(geo_df.groupby(trajectory_id_field)))
    trajectories = []
    for key, value in df_by_id.items():
        traj = Trajectory(key, value)
        trajectories.append(traj)
    return trajectories
