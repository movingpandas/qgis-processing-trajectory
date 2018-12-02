# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectory.py
    ---------------------
    Date                 : January 2018
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
__date__ = 'January 2018'
__copyright__ = '(C) 2018, Anita Graser'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import pandas as pd 
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate
from datetime import datetime, timedelta

class Trajectory():
    def __init__(self, id, df):
        self.id = id
        self.df = df
        
    def __str__(self):
        return "Trajectory {1} ({2} to {3}) | Size: {0}\n{4}".format(
            self.df.geometry.count(), self.id, self.get_start_time(), 
            self.get_end_time(), self.to_linestring().wkt)
        
    def to_linestring(self):
        return self.make_line(self.df)
        
    def get_start_time(self):
        return self.df.index.min()
        
    def get_end_time(self):
        return self.df.index.max()
        
    def get_position_at(self, t):
        try:
            return self.df.loc[t]['geometry'][0]
        except:
            #return self.df.iloc[self.df.index.get_loc(t, method='nearest')]['geometry']
            return self.df.iloc[self.df.index.drop_duplicates().get_loc(t, method='nearest')]['geometry']        
        
    def get_linestring_between(self, t1, t2):
        try:
            return self.make_line(self.get_segment_between(t1, t2))
        except RuntimeError:
            raise RuntimeError("Cannot generate linestring between {0} and {1}".format(t1, t2))
        
    def get_segment_between(self, t1, t2):
        return self.df[t1:t2]
        
    def make_line(self, df):
        if df.size > 1:
            return df.groupby([True]*len(df))['geometry'].apply(
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
        return LineString(list(pt0.coords)+list(pt1.coords))
        
    def to_line_df(self):
        line_df = self.df.copy()
        line_df['prev_pt'] = line_df['geometry'].shift()
        line_df['t'] = self.df.index
        line_df['prev_t'] = line_df['t'].shift()
        line_df['line'] = line_df.apply(self.connect_points, axis=1)
        return line_df.set_geometry('line')[1:]
    
    def get_spatiotemporal_ref(self, row):
        #print(type(row['geo_intersection']))
        if type(row['geo_intersection'])==LineString:
            pt0 = Point(row['geo_intersection'].coords[0])
            ptn = Point(row['geo_intersection'].coords[-1])
            t = row['prev_t']
            t_delta = row['t'] - t
            len = row['line'].length
            t0 = t + (t_delta * row['line'].project(pt0)/len)
            tn = t + (t_delta * row['line'].project(ptn)/len)
            # to avoid intersection issues with zero length lines
            if ptn == translate(pt0, 0.00000001, 0.00000001):
                t0 = t
                tn = row['t'] 
            return {'pt0':pt0,'ptn':ptn,'t0':t0,'tn':tn}
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
        #print(line_df['intersection'])
        j = 0
        t_ranges = []
        for index, row in line_df.iterrows():
            x = row['intersection']
            if x is None: 
                continue
            t_ranges.append((x['t0'], x['tn']))
            # create row at entry point with attributes from previous row = pad 
            row0 = self.df.iloc[self.df.index.drop_duplicates().get_loc(x['t0'], method='pad')]
            row0['geometry'] = x['pt0']
            # create row at exit point
            rown = self.df.iloc[self.df.index.drop_duplicates().get_loc(x['tn'], method='pad')]
            rown['geometry'] = x['ptn']
            # insert rows
            self.df.loc[x['t0']] = row0
            self.df.loc[x['tn']] = rown
            self.df = self.df.sort_index()
        t_ranges = self.dissolve_time_ranges(t_ranges)
        for t_range in t_ranges:
            #print(t_range)
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
            elif t_range[0] > end and t_range[0] - end < timedelta(milliseconds=10):
                end = t_range[1]
            else:
                new.append((start, end))
                start = t_range[0]
                end = t_range[1]
        new.append((start, end))
        return new

