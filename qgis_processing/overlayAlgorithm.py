import os
import sys

import shapely.wkt
from shapely.geometry import Polygon

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsFeature,
    QgsFeatureSink,
    QgsFeatureRequest,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterString,
    QgsProcessingParameterExtent,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterEnum,
    QgsWkbTypes,
)

sys.path.append("..")

from .qgisUtils import tc_to_sink, traj_to_sink
from .trajectoriesAlgorithm import TrajectoriesAlgorithm


class ClipTrajectoriesByExtentAlgorithm(TrajectoriesAlgorithm):
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

    def group(self):
        return self.tr("Overlay")

    def groupId(self):
        return "TrajectoryOverlay"

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

    def createInstance(self):
        return type(self)()

    def processTc(self, tc, parameters, context):
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        extent = shapely.wkt.loads(extent.asWktPolygon())
        tc = tc.clip(extent)
        tc_to_sink(tc, self.sink_pts, self.fields_pts, self.timestamp_field)
        for split in tc:
            traj_to_sink(split, self.sink_trajs)

        
