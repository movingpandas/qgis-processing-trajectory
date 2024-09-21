import sys
import pandas as pd

from movingpandas import (
    KalmanSmootherCV,
)

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
)

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm


class SmoothingAlgorithm(TrajectoryManipulationAlgorithm):
    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Trajectory smoothing")

    def groupId(self):
        return "TrajectorySmoothing"


class KalmanSmootherAlgorithm(SmoothingAlgorithm):
    PROCESS_NOISE = "PROCESS_NOISE"
    MEASURE_NOISE = "MEASURE_NOISE"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.PROCESS_NOISE,
                description=self.tr("Process (acceleration) noise standard deviation."),
                defaultValue=0.1,
                type=QgsProcessingParameterNumber.Double,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.MEASURE_NOISE,
                description=self.tr("Measurement noise standard deviation"),
                defaultValue=1,
                type=QgsProcessingParameterNumber.Double,
            )
        )

    def name(self):
        return "smooth_kalman"

    def displayName(self):
        return self.tr("Kalman filter with constant velocity model")

    def shortHelpString(self):
        return self.tr(
            "<p>Smooths trajectories using a Kalman Filter with a Constant Velocity model. "
            "The Constant Velocity model assumes that the speed between consecutive "
            "locations is nearly constant. For trajectories where traj.is_latlon = True "
            "the smoother converts to EPSG:3395 (World Mercator) internally to perform "
            "filtering and smoothing. "
            "<p>Higher <b>Process noise</b> values lead to less-smooth trajectories.</p>"
            "<p>Higher <b>Measurement noise</b> values lead to smoother trajectories.</p>"
            "<p>For more info see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorysmoother.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        pn = self.parameterAsDouble(parameters, self.PROCESS_NOISE, context)
        mn = self.parameterAsDouble(parameters, self.MEASURE_NOISE, context)
        smooth = KalmanSmootherCV(tc).smooth(process_noise_std=pn, measurement_noise_std=mn)
        self.tc_to_sink(smooth)
        for traj in smooth:
            self.traj_to_sink(traj)
