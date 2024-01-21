import sys

import shapely.wkt
from shapely.geometry import Polygon

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingParameterExtent,
    QgsProcessingParameterVectorLayer,
)

sys.path.append("..")

from .qgisUtils import tc_to_sink, traj_to_sink
from .trajectoriesAlgorithm import TrajectoriesAlgorithm


class OverlayTrajectoriesAlgorithm(TrajectoriesAlgorithm):
    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Trajectory overlay")

    def groupId(self):
        return "TrajectoryOverlay"


class ClipTrajectoriesByExtentAlgorithm(OverlayTrajectoriesAlgorithm):
    EXTENT = "EXTENT"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterExtent(
                name=self.EXTENT, description=self.tr("Extent"), optional=False
            )
        )

    def name(self):
        return "clip_traj_extent"

    def tr(self, text):
        return QCoreApplication.translate("clip_traj_extent", text)

    def displayName(self):
        return self.tr("Clip trajectories by extent")

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a trajectory point layers with speed and direction information "
            "as well as a trajectory line layer clipped by the specified extent.</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def helpUrl(self):
        return "https://movingpandas.org/units"

    def processTc(self, tc, parameters, context):
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        extent = shapely.wkt.loads(extent.asWktPolygon())
        clipped = tc.clip(extent)
        tc_to_sink(clipped, self.sink_pts, self.fields_pts, self.timestamp_field)
        for traj in clipped:
            traj_to_sink(traj, self.sink_trajs)


class ClipTrajectoriesByPolygonLayer(OverlayTrajectoriesAlgorithm):
    CLIP_LAYER = "CLIP_LAYER"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.CLIP_LAYER,
                description=self.tr("Overlay layer"),
                optional=False,
            )
        )

    def name(self):
        return "clip_traj_vector"

    def tr(self, text):
        return QCoreApplication.translate("clip_traj_vector", text)

    def displayName(self):
        return self.tr("Clip trajectories by polygon layer")

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a trajectory point layers with speed and direction information "
            "as well as a trajectory line layer clipped by the specified vector layer.</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def helpUrl(self):
        return "https://movingpandas.org/units"

    def processTc(self, tc, parameters, context):
        vlayer = self.parameterAsVectorLayer(parameters, self.CLIP_LAYER, context)
        for feature in vlayer.getFeatures():
            extent = shapely.wkt.loads(feature.geometry().asWkt())
            clipped = tc.clip(extent)
            tc_to_sink(clipped, self.sink_pts, self.fields_pts, self.timestamp_field)
            for traj in clipped:
                traj_to_sink(traj, self.sink_trajs)
