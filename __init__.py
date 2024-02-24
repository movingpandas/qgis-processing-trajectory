# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectoolsProviderPlugin.py
    ---------------------
    Date                 : February 2024
    Copyright            : (C) 2024 by Anita Graser
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
__date__ = 'Feb 2024'
__copyright__ = '(C) 2024, Anita Graser'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from .qgis_processing.trajectoolsProviderPlugin import TrajectoryProviderPlugin


def classFactory(iface):
    return TrajectoryProviderPlugin()
