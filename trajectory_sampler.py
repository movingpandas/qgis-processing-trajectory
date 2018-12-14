# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectory_sampler.py
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

import warnings
from pandas import NaT
from datetime import timedelta


class TrajectorySample():
    def __init__(self, id, start_timedelta, past_timedelta, future_timedelta, past_traj, future_pos):
        self.id = id
        self.start_secs = start_timedelta.total_seconds()
        self.past_secs = past_timedelta.total_seconds()
        self.future_secs = future_timedelta.total_seconds()
        self.past_traj = past_traj
        self.future_pos = future_pos
        
    def __str__(self):
        return str([self.id, self.start_secs, self.past_secs, self.future_secs, self.past_traj.to_linestring().wkt, self.future_pos.wkt])


class TrajectorySampler():
    def __init__(self, traj):
        self.traj = traj
        self.sample_counter = 0
        
    def get_sample(self, start_timedelta, past_timedelta, future_timedelta, min_meters_per_sec = 0.3):
        if self.traj.get_duration() < (start_timedelta + future_timedelta):
            raise RuntimeError("Trajectory is too short to extract sample of {} seconds!".format((start_timedelta + future_timedelta).total_seconds()))
        
        self.traj.add_meters_per_sec() 
        self.traj.df['next_ms'] = self.traj.df['meters_per_sec'].shift(-1)
        self.traj.df = self.traj.df[:-1]

        above_speed_limit = self.traj.df[self.traj.df['next_ms'] > min_meters_per_sec]
        if len(above_speed_limit) == 0:
            raise RuntimeError("No data above specified speed limit!")
            
        t0 = above_speed_limit.index.min().to_pydatetime().replace(microsecond=0) + timedelta(seconds=1)
        start_time = t0 + start_timedelta
        
        past_traj = self.traj.get_segment_between(start_time - past_timedelta, start_time)
        if not past_traj:
            raise RuntimeError("Failed to extract past trajectory!")
            
        future_pos = self.traj.get_position_at(start_time + future_timedelta)

        sample_id = "{}_{}".format(self.traj.id, self.sample_counter)
        self.sample_counter += 1
        return TrajectorySample(sample_id, start_timedelta, past_timedelta, future_timedelta, past_traj, future_pos)
        
        
    