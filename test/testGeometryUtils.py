# -*- coding: utf-8 -*-

"""
***************************************************************************
    testGeometryUtils.py
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
from shapely.geometry import Point

sys.path.append("..")

from trajectory import Trajectory 
from geometryUtils import azimuth
 
class TestGeometryUtils(unittest.TestCase):
 
    def test_azimuth(self):
        result = azimuth(Point(0,0), Point(1,0))
        expected_result = 90
        self.assertEqual(result, expected_result)
         
        result = azimuth(Point(0,0), Point(100,0))
        expected_result = 90
        self.assertEqual(result, expected_result) 
        
        result = azimuth(Point(0,0), Point(-10,0))
        expected_result = 270
        self.assertEqual(result, expected_result) 
        
        result = azimuth(Point(0,0), Point(0,1))
        expected_result = 0
        self.assertEqual(result, expected_result) 
            
        result = azimuth(Point(0,0), Point(0,-1))
        expected_result = 180
        self.assertEqual(result, expected_result) 
 
        result = azimuth(Point(0,0), Point(1, 1))
        expected_result = 45
        self.assertEqual(result, expected_result) 
        
        result = azimuth(Point(0,0), Point(1, -1))
        expected_result = 135
        self.assertEqual(result, expected_result) 
        
        result = azimuth(Point(0,0), Point(-1, -1))
        expected_result = 225
        self.assertEqual(result, expected_result) 
        
        result = azimuth(Point(100,100), Point(99, 101))
        expected_result = 315
        self.assertEqual(result, expected_result) 
        
        
if __name__ == '__main__':
    unittest.main()