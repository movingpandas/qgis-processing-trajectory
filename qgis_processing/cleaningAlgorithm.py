import sys
import pandas as pd

from movingpandas import (
    OutlierCleaner
)

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
)

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm


class CleaningAlgorithm(TrajectoryManipulationAlgorithm):

    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Trajectory cleaning")

    def groupId(self):
        return "TrajectoryCleaning"


class OutlierCleanerAlgorithm(CleaningAlgorithm):
    TOLERANCE = "TOLERANCE"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.TOLERANCE,
                description=self.tr("Speed threshold"),
                defaultValue=10.0,
                type=QgsProcessingParameterNumber.Double,
            )
        )

    def name(self):
        return "clean_vmax"

    def displayName(self):
        return self.tr("Remove speed above threshold")

    def shortHelpString(self):
        return self.tr(
            "<p>Speed-based outlier cleaner that cuts away spikes in the trajectory when "
            "the speed exceeds the provided speed threshold value </p>"
            "<p>For more info see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorycleaner.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        v_max = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        generalized = OutlierCleaner(tc).clean(v_max=v_max, units=tuple(self.speed_units))
        self.tc_to_sink(generalized)
        for traj in generalized:
            self.traj_to_sink(traj)
