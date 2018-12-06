# -*- coding: utf-8 -*-

"""
***************************************************************************
    geometryUtils.py
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


import math 
from shapely.geometry import Point


def azimuth(point1, point2):
    angle = math.atan2(point2.x - point1.x, point2.y - point1.y) 
    azimuth = math.degrees(angle)    
    if angle < 0:
        azimuth += 360
    #print("{}->{}: angle={} azimuth={}".format(point1, point2, angle, azimuth))
    return azimuth

