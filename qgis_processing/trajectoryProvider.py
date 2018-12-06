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

__author__ = 'Anita Graser'
__date__ = 'December 2018'
__copyright__ = '(C) 2018, Anita Graser'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

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
                AddHeadingAlgorithm()]
        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=''):
        pass
