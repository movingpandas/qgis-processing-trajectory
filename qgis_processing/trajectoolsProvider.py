import os
import sys

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingProvider, QgsMessageLog
from processing.core.ProcessingConfig import ProcessingConfig, Setting

sys.path.append("..")

from .createTrajectoriesAlgorithm import CreateTrajectoriesAlgorithm
from .splitTrajectoriesAlgorithm import (
    ObservationGapSplitterAlgorithm,
    TemporalSplitterAlgorithm,
    StopSplitterAlgorithm,
)
from .overlayAlgorithm import (
    ClipTrajectoriesByExtentAlgorithm,
    ClipTrajectoriesByPolygonLayerAlgorithm,
    IntersectWithPolygonLayerAlgorithm,
)
from .extractPtsAlgorithm import ExtractODPtsAlgorithm, ExtractStopsAlgorithm
from .privacyAttackAlgorithm import HomeWorkAttack
from .gtfsAlgorithm import GtfsAlgorithm

pluginPath = os.path.dirname(__file__)


class TrajectoolsProvider(QgsProcessingProvider):
    def __init__(self):
        super().__init__()
        self.algs = []

    def id(self):
        return "Trajectory"

    def name(self):
        return "Trajectools"

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
        algs = [
            CreateTrajectoriesAlgorithm(),
            ObservationGapSplitterAlgorithm(),
            TemporalSplitterAlgorithm(),
            StopSplitterAlgorithm(),
            ClipTrajectoriesByExtentAlgorithm(),
            ClipTrajectoriesByPolygonLayerAlgorithm(),
            IntersectWithPolygonLayerAlgorithm(),
            ExtractODPtsAlgorithm(),
            ExtractStopsAlgorithm(),
        ]
        try:  # skmob-based algs
            algs.append(HomeWorkAttack())
        except ImportError:
            pass
        try:  # gtfs_functions-based algs
            algs.append(GtfsAlgorithm())
        except ImportError:
            pass
        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=""):
        pass
