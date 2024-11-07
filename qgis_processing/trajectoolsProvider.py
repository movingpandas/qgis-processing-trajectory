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
from .extractPtsAlgorithm import (
    ExtractODPtsAlgorithm, 
    ExtractStopsAlgorithm,
)
from .generalizationAlgorithm import (
    DouglasPeuckerGeneralizerAlgorithm,
    MinDistanceGeneralizerAlgorithm,
    MinTimeDeltaGeneralizerAlgorithm,
    TopDownTimeRatioGeneralizerAlgorithm,
)
from .cleaningAlgorithm import (
    OutlierCleanerAlgorithm,
)

try:  # skmob-based algs
    from .privacyAttackAlgorithm import HomeWorkAttack
except ImportError:
    pass

try:  # gtfs_functions-based algs
    from .gtfsAlgorithm import (
        GtfsStopsAlgorithm,
        GtfsShapesAlgorithm, 
        GtfsSegmentsAlgorithm
    )
except ImportError:
    pass

try:  # stonesoup-based algs
    from .smoothingAlgorithm import KalmanSmootherAlgorithm
except ImportError:
    pass


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
            DouglasPeuckerGeneralizerAlgorithm(),
            MinDistanceGeneralizerAlgorithm(),
            MinTimeDeltaGeneralizerAlgorithm(),
            TopDownTimeRatioGeneralizerAlgorithm(),
            OutlierCleanerAlgorithm(),
        ]
        try:  # skmob-based algs
            algs.append(HomeWorkAttack())
        except NameError:
            pass
        try:  # gtfs_functions-based algs
            algs.append(GtfsStopsAlgorithm())
            algs.append(GtfsShapesAlgorithm())
            algs.append(GtfsSegmentsAlgorithm())
        except NameError:
            pass
        try:  # stonesoup-based algs
            algs.append(KalmanSmootherAlgorithm())
        except NameError:
            pass
        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=""):
        pass
