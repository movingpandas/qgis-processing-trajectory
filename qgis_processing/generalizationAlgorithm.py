import sys
import pandas as pd

from movingpandas import (
    DouglasPeuckerGeneralizer,
    MinDistanceGeneralizer,
    MinTimeDeltaGeneralizer,
    TopDownTimeRatioGeneralizer,
)

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
)

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm


class GeneralizeTrajectoriesAlgorithm(TrajectoryManipulationAlgorithm):
    TOLERANCE = "TOLERANCE"

    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Trajectory generalization")

    def groupId(self):
        return "TrajectoryGeneralization"


class DouglasPeuckerGeneralizerAlgorithm(GeneralizeTrajectoriesAlgorithm):
    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.TOLERANCE,
                description=self.tr("Distance tolerance in trajectory CRS units"),
                defaultValue=10.0,
                type=QgsProcessingParameterNumber.Double,
            )
        )

    def name(self):
        return "generalize_dp"

    def displayName(self):
        return self.tr("Douglas-Peucker generalization")

    def shortHelpString(self):
        return self.tr(
            "<p>Generalizes trajectories using Douglas-Peucker algorithm "
            "(as implemented in shapely/Geos). </p>"
            "<p>For more info see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorygeneralizer.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        tolerance = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        generalized = DouglasPeuckerGeneralizer(tc).generalize(tolerance)
        self.tc_to_sink(generalized)
        for traj in generalized:
            self.traj_to_sink(traj)


class MinDistanceGeneralizerAlgorithm(GeneralizeTrajectoriesAlgorithm):
    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.TOLERANCE,
                description=self.tr("Distance tolerance"),
                defaultValue=10.0,
                type=QgsProcessingParameterNumber.Double,
            )
        )

    def name(self):
        return "generalize_min_dist"

    def displayName(self):
        return self.tr("Distance-based generalization")

    def shortHelpString(self):
        return self.tr(
            "This generalization ensures that consecutive locations are at least a "
            "certain distance apart. "
            "Distance is calculated using CRS units, except if the CRS is geographic "
            "(e.g. EPSG:4326 WGS84) then distance is calculated in metres. </p>"
            "<p>For more info see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorygeneralizer.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        tolerance = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        generalized = MinDistanceGeneralizer(tc).generalize(tolerance)
        self.tc_to_sink(generalized)
        for traj in generalized:
            self.traj_to_sink(traj)


class MinTimeDeltaGeneralizerAlgorithm(GeneralizeTrajectoriesAlgorithm):
    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TOLERANCE,
                description=self.tr(
                    "Time tolerance (timedelta, e.g. 1 hours, 15 minutes)"
                ),
                defaultValue="2 minutes",
                optional=False,
            )
        )

    def name(self):
        return "generalize_min_timedelta"

    def displayName(self):
        return self.tr("Temporal generalization")

    def shortHelpString(self):
        return self.tr(
            "This generalization ensures that consecutive rows are at least a certain "
            "timedelta apart. </p>"
            "<p>For more info see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorygeneralizer.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        tolerance = self.parameterAsString(parameters, self.TOLERANCE, context)
        tolerance = pd.Timedelta(tolerance).to_pytimedelta()
        generalized = MinTimeDeltaGeneralizer(tc).generalize(tolerance)
        self.tc_to_sink(generalized)
        for traj in generalized:
            self.traj_to_sink(traj)


class TopDownTimeRatioGeneralizerAlgorithm(GeneralizeTrajectoriesAlgorithm):
    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.TOLERANCE,
                description=self.tr("Distance tolerance in trajectory CRS units"),
                defaultValue=10.0,
                type=QgsProcessingParameterNumber.Double,
            )
        )

    def name(self):
        return "generalize_topdown"

    def displayName(self):
        return self.tr("Spatiotemporal generalization (TDTR)")

    def shortHelpString(self):
        return self.tr(
            "Generalizes using Top-Down Time Ratio algorithm proposed by "
            "Meratnia & de By (2004). "
            "This is a spatiotemporal trajectory generalization algorithm. "
            "Where Douglas-Peucker simply measures the spatial distance between points "
            "and original line geometry, Top-Down Time Ratio (TDTR) measures the distance "
            "between points and their spatiotemporal projection on the trajectory. "
            "These projections are calculated based on the ratio of travel times between "
            "the segment start and end times and the point time. </p>"
            "<p>For more info see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorygeneralizer.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        tolerance = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        generalized = TopDownTimeRatioGeneralizer(tc).generalize(tolerance)
        self.tc_to_sink(generalized)
        for traj in generalized:
            self.traj_to_sink(traj)
