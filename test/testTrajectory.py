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

or if you want to run all tests at once:

python3 -m unittest discover . -v

"""

import sys 
import unittest
import pandas as pd 
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate
from datetime import datetime, timedelta
from numpy import nan

sys.path.append("..")

from trajectory import Trajectory 

 
class TestTrajectory(unittest.TestCase):
 
    def test_linestring_wkt(self):
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,10,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        result = traj.to_linestring().wkt
        expected_result = "LINESTRING (0 0, 6 0, 10 0)"        
        self.assertEqual(result, expected_result) 
        
    def test_linstring_m_wkt(self):
        data = [{'geometry':Point(0,0), 't':datetime(1970,1,1,0,0,1)},
                {'geometry':Point(6,0), 't':datetime(1970,1,1,0,0,2)},
                {'geometry':Point(10,0), 't':datetime(1970,1,1,0,0,3)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        result = traj.to_linestringm_wkt()
        expected_result = "LINESTRING M (0.0 0.0 1.0, 6.0 0.0 2.0, 10.0 0.0 3.0)"        
        self.assertEqual(result, expected_result) 
         
    def test_two_intersections_with_same_polygon(self):
        polygon = Polygon([(5,-5), (7,-5), (7,12), (5,12), (5,-5)])
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
                {'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        intersections = traj.intersection(polygon)
        # spatial 
        result = []
        for x in intersections:
            result.append(x.to_linestring().wkt)
        expected_result = ["LINESTRING (5 0, 6 0, 7 0)", "LINESTRING (7 10, 5 10)"]
        self.assertEqual(result, expected_result)
        # temporal 
        result = []
        for x in intersections:
            result.append((x.get_start_time(), x.get_end_time()))
        expected_result = [(datetime(2018,1,1,12,5,0), datetime(2018,1,1,12,7,0)),
                           (datetime(2018,1,1,12,39,0), datetime(2018,1,1,12,45,0))]
        self.assertEqual(result, expected_result) 
                
    def test_intersection_with_duplicate_traj_points(self):
        polygon = Polygon([(5,-5), (7,-5), (7,5), (5,5), (5,-5)])
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,7,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,11,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
                {'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
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
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
                {'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'} )
        traj = Trajectory(1,geo_df)        
        intersections = traj.intersection(polygon)
        # spatial
        result = []
        for x in intersections:
            result.append(x.to_linestring().wkt)
        expected_result = ["LINESTRING (5 0, 6 0, 7 0)"]
        self.assertEqual(result, expected_result)
        # temporal
        result = []
        for x in intersections:
            result.append((x.get_start_time(), x.get_end_time()))
        expected_result = [(datetime(2018,1,1,12,5,0), datetime(2018,1,1,12,7,0))]
        self.assertEqual(result, expected_result) 
         
    def test_one_intersection_reversed(self):
        polygon = Polygon([(5,-5), (7,-5), (7,5), (5,5), (5,-5)])
        data = [{'geometry':Point(0,10), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,6,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,30,0)},
                {'geometry':Point(0,0), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'} )
        traj = Trajectory(1,geo_df)   
        intersections = traj.intersection(polygon)
        # spatial
        result = []
        for x in intersections:
            result.append(x.to_linestring().wkt)
        expected_result = ["LINESTRING (7 0, 6 0, 5 0)"]
        self.assertEqual(result, expected_result)
        # temporal
        result = []
        for x in intersections:
            result.append((x.get_start_time(), x.get_end_time()))
        expected_result = [(datetime(2018,1,1,12,25,0), datetime(2018,1,1,12,35,0))]
        self.assertEqual(result, expected_result) 
         
    def test_intersection_with_milliseconds(self):
        polygon = Polygon([(5,-5), (7,-5), (8,5), (5,5), (5,-5)])
        data = [{'geometry':Point(0,10), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,15,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,30,0)},
                {'geometry':Point(0,0), 't':datetime(2018,1,1,13,0,0)}]
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
         
    def test_intersection_with_numerical_time_issues(self):     
        xmin, xmax, ymin, ymax = 116.36850352835575,116.37029459899574,39.904675309969896,39.90772814977718 
        polygon = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)])
        data = [{'geometry':Point(116.36855, 39.904926), 't':datetime(2009,3,10,11,3,35)},
                {'geometry':Point(116.368612, 39.904877), 't':datetime(2009,3,10,11,3,37)},
                {'geometry':Point(116.368644, 39.90484), 't':datetime(2009,3,10,11,3,39)}]        
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        intersection = traj.intersection(polygon)[0]
        result = intersection.to_linestring().wkt
        expected_result = "LINESTRING (116.36855 39.904926, 116.368612 39.904877, 116.368644 39.90484)"
        self.assertEqual(result, expected_result)         
         
    def test_no_intersection(self):
        polygon = Polygon([(105,-5), (107,-5), (107,12), (105,12), (105,-5)])
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,15,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
                {'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        result = traj.intersection(polygon)
        expected_result = []
        self.assertEqual(result, expected_result) 

    def test_get_position_at_existing_timestamp(self):
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,20,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        result = traj.get_position_at(datetime(2018,1,1,12,10,0))      
        expected_result = Point(6,0)
        self.assertEqual(result, expected_result)

    def test_get_position_of_nearest_timestamp(self):
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,20,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        result = traj.get_position_at(datetime(2018,1,1,12,14,0))      
        expected_result = Point(6,0)
        self.assertEqual(result, expected_result)
        result = traj.get_position_at(datetime(2018,1,1,12,15,0))      
        expected_result = Point(10,0)
        self.assertEqual(result, expected_result)
        
    def test_get_segment_between_existing_timestamps(self):
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,15,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)},
                {'geometry':Point(0,10), 't':datetime(2018,1,1,13,0,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        result = traj.get_segment_between(datetime(2018,1,1,12,10,0),datetime(2018,1,1,12,30,0))
        data = [{'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,15,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,0)}]
        expected_result = pd.DataFrame(data).set_index('t')
        pd.testing.assert_frame_equal(result, expected_result)
        data = [{'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(10,0), 't':datetime(2018,1,1,12,15,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,30,1)}]
        expected_result = pd.DataFrame(data).set_index('t')
        self.assertNotEqual(result.to_dict(), expected_result.to_dict()) 
        
    def test_add_heading(self):
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,10,0)},
                {'geometry':Point(6,-6), 't':datetime(2018,1,1,12,20,0)},
                {'geometry':Point(-6,-6), 't':datetime(2018,1,1,12,20,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        traj.add_heading()
        result = traj.df['heading'].tolist() 
        expected_result = [90.0, 90.0, 180.0, 270]
        self.assertEqual(result, expected_result)
        
    def test_add_heading_latlon(self):
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(10,10), 't':datetime(2018,1,1,12,10,0)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '4326'})
        traj = Trajectory(1,geo_df)
        traj.add_heading()
        result = traj.df['heading'].tolist()
        expected_result = [44.561451413257714, 44.561451413257714]
        self.assertAlmostEqual(result[0], expected_result[0], 5)
        
    def test_add_meters_per_sec(self):
        data = [{'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,0,1)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '31256'})
        traj = Trajectory(1,geo_df)
        traj.add_meters_per_sec()
        result = traj.df['meters_per_sec'].tolist() 
        expected_result = [6.0, 6.0]
        self.assertEqual(result, expected_result)
        
    def test_add_meters_per_sec_latlon(self):
        data = [{'geometry':Point(0,1), 't':datetime(2018,1,1,12,0,0)},
                {'geometry':Point(6,0), 't':datetime(2018,1,1,12,0,1)}]
        df = pd.DataFrame(data).set_index('t')
        geo_df = GeoDataFrame(df, crs={'init': '4326'})
        traj = Trajectory(1,geo_df)
        traj.add_meters_per_sec()
        result = traj.df['meters_per_sec'].tolist()[0]/1000
        expected_result = 676.3
        self.assertAlmostEqual(result, expected_result, 1)
        
 
if __name__ == '__main__':
    unittest.main()