# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectory.py
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

import os
import sys
import pandas as pd 
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(__file__))

from geometryUtils import azimuth, calculate_initial_compass_bearing, measure_distance_spherical, measure_distance_euclidean


def to_unixtime(t):
    return (t - datetime(1970,1,1,0,0,0)).total_seconds() 

def is_equal(t1, t2):
    return abs(t1 - t2) < timedelta(milliseconds=10)


class Trajectory():
    def __init__(self, id, df):
        self.id = id
        self.df = df
        self.crs = df.crs['init']
        
    def __str__(self):
        return "Trajectory {1} ({2} to {3}) | Size: {0}\n{4}".format(
            self.df.geometry.count(), self.id, self.get_start_time(), 
            self.get_end_time(), self.to_linestring().wkt)
        
    def to_linestring(self):
        return self.make_line(self.df)
    
    def to_linestringm_wkt(self):
        # Shapely only supports x, y, z. Therfore, this is a bit hacky!
        coords = ''
        for index, row in self.df.iterrows():
            pt = row.geometry
            t = to_unixtime(index)
            coords += "{} {} {}, ".format(pt.x, pt.y, t)  
        wkt = "LINESTRING M ({})".format(coords[:-2])
        return wkt
        
    def get_start_location(self):
        return self.df.head(1).geometry[0]
    
    def get_end_location(self):
        return self.df.tail(1).geometry[0]
        
    def get_start_time(self):
        return self.df.index.min().to_pydatetime()
        
    def get_end_time(self):
        return self.df.index.max().to_pydatetime()
        
    def get_position_at(self, t):
        try:
            return self.df.loc[t].geometry[0]
        except:
            #return self.df.iloc[self.df.index.get_loc(t, method='nearest')]['geometry']
            return self.df.iloc[self.df.index.drop_duplicates().get_loc(t, method='nearest')].geometry       
        
    def get_linestring_between(self, t1, t2):
        try:
            return self.make_line(self.get_segment_between(t1, t2))
        except RuntimeError:
            raise RuntimeError("Cannot generate linestring between {0} and {1}".format(t1, t2))
        
    def get_segment_between(self, t1, t2):
        return self.df[t1:t2]

    def compute_heading(self, row):
        pt0 = row['prev_pt']
        pt1 = row['geometry']
        if type(pt0) != Point:
            return 0.0
        if pt0 == pt1:
            return 0.0
        if self.crs == '4326':
            return calculate_initial_compass_bearing(pt0, pt1)            
        else:
            return azimuth(pt0, pt1)
        
    def compute_speed(self, row):
        pt0 = row['prev_pt']
        pt1 = row['geometry']
        if type(pt0) != Point:
            return 0.0
        if pt0 == pt1:
            return 0.0
        if self.crs == '4326':
            dist_meters = measure_distance_spherical(pt0, pt1)
        else: # The following distance will be in CRS units that might not be meters!
            dist_meters = measure_distance_euclidean(pt0, pt1)
        return dist_meters / row['delta_t'].total_seconds()  
            
    def add_heading(self):
        self.df['prev_pt'] = self.df.geometry.shift()
        self.df['heading'] = self.df.apply(self.compute_heading, axis=1)
        self.df.at[self.get_start_time(),'heading'] = self.df.iloc[1]['heading']
        
    def add_meters_per_sec(self):
        self.df['prev_pt'] = self.df.geometry.shift()
        self.df['t'] = self.df.index
        self.df['prev_t'] = self.df['t'].shift()
        self.df['delta_t'] = self.df['t'] - self.df['prev_t'] 
        self.df['meters_per_sec'] = self.df.apply(self.compute_speed, axis=1)
        self.df.at[self.get_start_time(),'meters_per_sec'] = self.df.iloc[1]['meters_per_sec']
        
    def make_line(self, df):
        if df.size > 1:
            return df.groupby([True]*len(df)).geometry.apply(
                lambda x: LineString(x.tolist())).values[0]
        else:
            raise RuntimeError('Dataframe needs at least two points to make line!') 
    
    def connect_points(self, row):
        pt0 = row['prev_pt']
        pt1 = row['geometry']
        if type(pt0) != Point:
            return None
        if pt0 == pt1:
            # to avoid intersection issues with zero length lines
            pt1 = translate(pt1, 0.00000001, 0.00000001)
        return LineString(list(pt0.coords) + list(pt1.coords))
        
    def to_line_df(self):
        line_df = self.df.copy()
        line_df['prev_pt'] = line_df['geometry'].shift()
        line_df['t'] = self.df.index
        line_df['prev_t'] = line_df['t'].shift()
        line_df['line'] = line_df.apply(self.connect_points, axis=1)
        return line_df.set_geometry('line')[1:]
    
    def get_spatiotemporal_ref(self, row):
        #print(type(row['geo_intersection']))
        if type(row['geo_intersection']) == LineString:
            pt0 = Point(row['geo_intersection'].coords[0])
            ptn = Point(row['geo_intersection'].coords[-1])
            t = row['prev_t']
            t_delta = row['t'] - t
            len = row['line'].length
            t0 = t + (t_delta * row['line'].project(pt0)/len)
            tn = t + (t_delta * row['line'].project(ptn)/len)
            # to avoid intersection issues with zero length lines
            if ptn == translate(pt0, 0.00000001, 0.00000001):
                t0 = row['prev_t']
                tn = row['t']
            # to avoid numerical issues with timestamps
            if is_equal(tn, row['t']):
                tn = row['t']
            if is_equal(t0, row['prev_t']):
                t0 = row['prev_t']
            return {'pt0':pt0, 'ptn':ptn, 't0':t0, 'tn':tn}
        else:
            return None
            
    def intersects(self, polygon):
        return self.to_linestring().intersects(polygon)
    
    def intersection(self, polygon):
        if not self.intersects(polygon):
            return []
        intersections = [] # list of trajectories
        # Note: If the trajectory contains consecutive rows without location change 
        #       these will result in zero length lines that return an empty 
        #       intersection.
        line_df = self.to_line_df()
        line_df['geo_intersection'] = line_df.intersection(polygon)
        line_df['intersection'] = line_df.apply(self.get_spatiotemporal_ref, axis=1)
        #pd.set_option('display.max_colwidth', -1)
        j = 0
        t_ranges = []
        # For unknown reasons, the following for loop creates wrong results if there 
        # is no other column besides the geometry column.
        has_dummy = False
        if len(self.df.columns) < 2:
            self.df['dummy_that_stops_things_from_breaking'] = 1
            has_dummy = True
        for index, row in line_df.iterrows():
            x = row['intersection']
            if x is None: 
                continue
            t_ranges.append((x['t0'], x['tn']))
            # Create row at entry point with attributes from previous row = pad 
            row0 = self.df.iloc[self.df.index.drop_duplicates().get_loc(x['t0'], method='pad')]
            row0['geometry'] = x['pt0']
            # Create row at exit point
            rown = self.df.iloc[self.df.index.drop_duplicates().get_loc(x['tn'], method='pad')]
            rown['geometry'] = x['ptn']
            # Insert rows
            self.df.loc[x['t0']] = row0
            self.df.loc[x['tn']] = rown
            self.df = self.df.sort_index()
        t_ranges = self.dissolve_time_ranges(t_ranges)
        if has_dummy:
            self.df.drop(columns=['dummy_that_stops_things_from_breaking'])
        for t_range in t_ranges:
            df = self.get_segment_between(t_range[0], t_range[1])
            intersections.append(Trajectory("{}_{}".format(self.id, j), df))
            j += 1
        return intersections
    
    def dissolve_time_ranges(self, t_ranges):
        new = []
        start = None
        end = None
        for t_range in t_ranges:
            if start is None:
                start = t_range[0]
                end = t_range[1]
            elif end == t_range[0]:
                end = t_range[1]
            elif t_range[0] > end and is_equal(t_range[0], end):
                end = t_range[1]
            else:
                new.append((start, end))
                start = t_range[0]
                end = t_range[1]
        new.append((start, end))
        return new

