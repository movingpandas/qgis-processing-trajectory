# -*- coding: utf-8 -*-

"""
***************************************************************************
    testTrajectory.py
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

ATTENTION!
If you use OSGeo4W, you need to run the following command first:
call C:\OSGeo4W64\bin\py3_env.bat

python3 testTrajectory.py -v

"""

import os
import sys 
import unittest
import pandas as pd 
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate
from datetime import datetime, timedelta
from numpy import nan

pluginPath = os.path.dirname(__file__)
sys.path.append(os.path.join(pluginPath,".."))

from trajectory import Trajectory 
 
data = [{'id':1, 'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
    {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
    {'id':1, 'geometry':Point(6,-6), 't':datetime(2018,1,1,12,20,0)},
    {'id':1, 'geometry':Point(-6,-6), 't':datetime(2018,1,1,12,20,0)}]
df = pd.DataFrame(data).set_index('t')
geo_df = GeoDataFrame(df, crs={'init': '31256'})
traj = Trajectory(1,geo_df)
traj.add_heading()

for index, row in df.iterrows():
    print(index)
    print(row['geometry'].wkt)
    print(row)
    



 