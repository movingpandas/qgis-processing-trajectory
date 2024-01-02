import sys

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsField,
    QgsGeometry,
    QgsFeature,
    QgsFeatureSink,
    QgsProcessingParameterString,
    QgsWkbTypes,
)

sys.path.append("..")

from .qgisUtils import tc_to_sink, traj_to_sink
from .trajectoriesAlgorithm import TrajectoriesAlgorithm


class CreateTrajectoriesAlgorithm(TrajectoriesAlgorithm):
    SPEED_UNIT = "SPEED_UNIT"

    def __init__(self):
        super().__init__()

    def name(self):
        return "create_trajectory"

    def tr(self, text):
        return QCoreApplication.translate("create_trajectory", text)

    def displayName(self):
        return self.tr("Create trajectories")

    def group(self):
        return self.tr("Basic")

    def groupId(self):
        return "TrajectoryBasic"

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a trajectory point layers with speed and direction information "
            "as well as a trajectory line layer.</p>"
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
        tc_to_sink(tc, self.sink_pts, self.fields_pts, self.timestamp_field)
        for traj in tc.trajectories:
            traj_to_sink(traj, self.sink_trajs)
