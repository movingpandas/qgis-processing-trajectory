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

__author__ = 'Anita Graser'
__date__ = 'December 2018'
__copyright__ = '(C) 2018, Anita Graser'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import sys 
import pandas as pd 
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate
from datetime import datetime, timedelta

sys.path.append("..")

from processing_trajectory.trajectory import Trajectory


def trajectories_from_qgis_point_layer(layer, time_field_name, trajectory_id_field, time_format):
    names = [field.name() for field in layer.fields()]
    data = []
    for feature in layer.getFeatures():
        my_dict = {}
        for i, a in enumerate(feature.attributes()):
            if names[i] == time_field_name:
                my_dict[names[i]] = datetime.strptime(a, time_format)
            else:
                my_dict[names[i]] = a
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        my_dict['geometry']=Point((x,y))
        data.append(my_dict)
    df = pd.DataFrame(data).set_index(time_field_name)
    crs = {'init': layer.sourceCrs().geographicCrsAuthId()} 
    geo_df = GeoDataFrame(df, crs=crs)
    #print(geo_df)
    df_by_id = dict(tuple(geo_df.groupby(trajectory_id_field)))
    trajectories = []
    for key, value in df_by_id.items():
        traj = Trajectory(key, value)
        trajectories.append(traj)
    return trajectories
