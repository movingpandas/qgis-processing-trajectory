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

import sys 
import unittest
import pandas as pd 
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate
from datetime import datetime, timedelta

sys.path.append("..")

from trajectory import Trajectory 
 
class TestTrajectory(unittest.TestCase):
 
    def test_two_intersections_with_same_polygon(self):
        polygon = Polygon([(5,-5), (7,-5), (7,12), (5,12), (5,-5)])
        data = [{'id':1, 'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
            {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
            {'id':1, 'geometry':Point(10,0), 't':datetime(2018,1,1,12,10,0)},
            {'id':1, 'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
            {'id':1, 'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        intersections = traj.intersection(polygon)
        # spatial 
        result = []
        for x in intersections:
            result.append(x.to_linestring())
        expected_result = [LineString([(5,0),(6,0),(7,0)]), LineString([(7,10),(5,10)])]
        self.assertEqual(result, expected_result)
        # temporal 
        result = []
        for x in intersections:
            result.append((x.get_start_time(), x.get_end_time()))
        expected_result = [(datetime(2018,1,1,12,5,0), datetime(2018,1,1,12,7,0)),
                           (datetime(2018,1,1,12,39,0), datetime(2018,1,1,12,45,0))]
        self.assertEqual(result, expected_result) 
        
                
    def test_duplicate_traj_points(self):
        polygon = Polygon([(5,-5), (7,-5), (7,5), (5,5), (5,-5)])
        data = [{'id':1, 'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
            {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
            {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,7,0)},
            {'id':1, 'geometry':Point(10,0), 't':datetime(2018,1,1,12,11,0)},
            {'id':1, 'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
            {'id':1, 'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'} )
        traj = Trajectory(1,geo_df)
        intersections = traj.intersection(polygon)
        # spatial
        result = []
        for x in intersections:
            result.append(x.to_linestring())
        expected_result = [LineString([(5,0),(6,0),(6,0),(7,0)])]
        self.assertEqual(result, expected_result)
        # temporal
        result = []
        for x in intersections:
            result.append((x.get_start_time(), x.get_end_time()))
        expected_result = [(datetime(2018,1,1,12,5,0), datetime(2018,1,1,12,8,0))]
        self.assertEqual(result, expected_result) 
         
 
    def test_one_intersection(self):
        polygon = Polygon([(5,-5), (7,-5), (7,5), (5,5), (5,-5)])
        data = [{'id':1, 'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
            {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
            {'id':1, 'geometry':Point(10,0), 't':datetime(2018,1,1,12,10,0)},
            {'id':1, 'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
            {'id':1, 'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'} )
        traj = Trajectory(1,geo_df)        
        intersections = traj.intersection(polygon)
        # spatial
        result = []
        for x in intersections:
            result.append(x.to_linestring())
        expected_result = [LineString([(5,0),(6,0),(7,0)])]
        self.assertEqual(result, expected_result)
        # temporal
        result = []
        for x in intersections:
            result.append((x.get_start_time(), x.get_end_time()))
        expected_result = [(datetime(2018,1,1,12,5,0), datetime(2018,1,1,12,7,0))]
        self.assertEqual(result, expected_result) 
         
     
    def test_one_intersection_reversed(self):
        polygon = Polygon([(5,-5), (7,-5), (7,5), (5,5), (5,-5)])
        data = [{'id':1, 'geometry':Point(0,10), 't':datetime(2018,1,1,12,0,0)},
            {'id':1, 'geometry':Point(10,10), 't':datetime(2018,1,1,12,6,0)},
            {'id':1, 'geometry':Point(10,0), 't':datetime(2018,1,1,12,10,0)},
            {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,30,0)},
            {'id':1, 'geometry':Point(0,0), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'} )
        traj = Trajectory(1,geo_df)   
        intersections = traj.intersection(polygon)
        # spatial
        result = []
        for x in intersections:
            result.append(x.to_linestring())
        expected_result = [LineString([(7,0),(6,0),(5,0)])]
        self.assertEqual(result, expected_result)
        # temporal
        result = []
        for x in intersections:
            result.append((x.get_start_time(), x.get_end_time()))
        expected_result = [(datetime(2018,1,1,12,25,0), datetime(2018,1,1,12,35,0))]
        self.assertEqual(result, expected_result) 
         
     
    def test_milliseconds(self):
        polygon = Polygon([(5,-5), (7,-5), (8,5), (5,5), (5,-5)])
        data = [{'id':1, 'geometry':Point(0,10), 't':datetime(2018,1,1,12,0,0)},
            {'id':1, 'geometry':Point(10,10), 't':datetime(2018,1,1,12,10,0)},
            {'id':1, 'geometry':Point(10,0), 't':datetime(2018,1,1,12,15,0)},
            {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,30,0)},
            {'id':1, 'geometry':Point(0,0), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'} )
        traj = Trajectory(1,geo_df)
        intersection = traj.intersection(polygon)[0]
        # spatial
        result = intersection.to_linestring().wkt
        expected_result = "LINESTRING (7.5 0, 6 0, 5 0)"
        self.assertEqual(result, expected_result)
        # temporal
        self.assertAlmostEqual(intersection.get_start_time(), datetime(2018,1,1,12,24,22,500000), delta=timedelta(milliseconds=1))
        self.assertEqual(intersection.get_end_time(), datetime(2018,1,1,12,35,0))
         
         
    def test_no_intersection(self):
        polygon = Polygon([(105,-5), (107,-5), (107,12), (105,12), (105,-5)])
        data = [{'id':1, 'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
            {'id':1, 'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
            {'id':1, 'geometry':Point(10,0), 't':datetime(2018,1,1,12,15,0)},
            {'id':1, 'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
            {'id':1, 'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        result = traj.intersection(polygon)
        expected_result = []
        self.assertEqual(result, expected_result) 

 
if __name__ == '__main__':
    unittest.main()