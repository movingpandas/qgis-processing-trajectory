# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectoryProviderPlugin.py
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

from qgis.core import QgsApplication

sys.path.append("..")

from .trajectoryProvider import TrajectoryProvider


class TrajectoryProviderPlugin:

    def __init__(self):
        self.provider = TrajectoryProvider()

    def initGui(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
