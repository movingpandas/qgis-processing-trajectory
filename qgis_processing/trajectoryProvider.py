# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectoryProvider.py
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

import os
import sys 

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingProvider, QgsMessageLog
from processing.core.ProcessingConfig import ProcessingConfig, Setting

sys.path.append("..")

from .trajectoriesFromPointLayerAlgorithm import TrajectoriesFromPointLayerAlgorithm
from .clipTrajectoriesByExtentAlgorithm import ClipTrajectoriesByExtentAlgorithm
from .addHeadingAlgorithm import AddHeadingAlgorithm
from .addMetersPerSecAlgorithm import AddMetersPerSecAlgorithm
from .splitOnDayBreakAlgorithm import SplitOnDayBreakAlgorithm

pluginPath = os.path.dirname(__file__)


class TrajectoryProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()
        self.algs = []

    def id(self):
        return "Trajectory"

    def name(self):
        return "Trajectory tools for Processing"

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))

    def load(self):
        self.refreshAlgorithms()
        return True

    def unload(self):
        pass

    def isActive(self):
        return True

    def setActive(self, active):
        pass

    def getAlgs(self):
        algs = [TrajectoriesFromPointLayerAlgorithm(),
                ClipTrajectoriesByExtentAlgorithm(),
                AddHeadingAlgorithm(),
                AddMetersPerSecAlgorithm(),
                SplitOnDayBreakAlgorithm()
                ]
        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=''):
        pass
