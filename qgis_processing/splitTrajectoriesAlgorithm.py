import sys
import pandas as pd

from movingpandas import TemporalSplitter, ObservationGapSplitter, StopSplitter

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
)

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoriesAlgorithm


class SplitTrajectoriesAlgorithm(TrajectoriesAlgorithm):
    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Split trajectories")

    def groupId(self):
        return "split_trajectories"


class ObservationGapSplitterAlgorithm(SplitTrajectoriesAlgorithm):
    TIME_GAP = "TIME_GAP"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TIME_GAP,
                description=self.tr("Time gap (timedelta, e.g. 1 hours, 15 minutes)"),
                defaultValue="1 hours",
                optional=True,
            )
        )

    def name(self):
        return "split_gap"

    def displayName(self):
        return self.tr("Split trajectories at observation gaps")

    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories "
            "whenever there is a gap in the observations "
            "(for supported time gap formats see: "
            "https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_timedelta.html)</p>"
            "<p>For more information on trajectory splitters see: "
            "https://movingpandas.readthedocs.io/en/main/trajectorysplitter.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        time_gap = self.parameterAsString(parameters, self.TIME_GAP, context)
        time_gap = pd.Timedelta(time_gap).to_pytimedelta()
        for traj in tc.trajectories:
            splits = ObservationGapSplitter(traj).split(gap=time_gap)
            self.tc_to_sink(splits)
            for split in splits:
                self.traj_to_sink(split)


class TemporalSplitterAlgorithm(SplitTrajectoriesAlgorithm):
    SPLIT_MODE = "SPLIT_MODE"
    SPLIT_MODE_OPTIONS = [
        "year",
        "month",
        "day",
        "hour",
    ]

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.SPLIT_MODE,
                description=self.tr("Splitting mode"),
                defaultValue="day",
                options=self.SPLIT_MODE_OPTIONS,
                optional=False,
            )
        )

    def name(self):
        return "split_temporally"

    def displayName(self):
        return self.tr("Split trajectories at time intervals")

    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories "
            "using regular time intervals (year, month, day, hour). </p>"
            "<p>For more information on trajectory splitters see: "
            "https://movingpandas.readthedocs.io/en/main/trajectorysplitter.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        split_mode = self.parameterAsInt(parameters, self.SPLIT_MODE, context)
        split_mode = self.SPLIT_MODE_OPTIONS[split_mode]
        for traj in tc.trajectories:
            splits = TemporalSplitter(traj).split(mode=split_mode)
            self.tc_to_sink(splits)
            for split in splits:
                self.traj_to_sink(split)


class StopSplitterAlgorithm(SplitTrajectoriesAlgorithm):
    MAX_DIAMETER = "MAX_DIAMETER"
    MIN_DURATION = "MIN_DURATION"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.MAX_DIAMETER,
                description=self.tr("Max stop diameter (meters)"),
                defaultValue=15,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.MIN_DURATION,
                description=self.tr(
                    "Min stop duration (timedelta, e.g. 1 hours, 15 minutes)"
                ),
                defaultValue="15 minutes",
                optional=False,
            )
        )

    def name(self):
        return "split_stops"

    def displayName(self):
        return self.tr("Split trajectories at stops")

    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories at stops. </p>"
            "<p>For more information on trajectory splitters see: "
            "https://movingpandas.readthedocs.io/en/main/trajectorysplitter.html</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def processTc(self, tc, parameters, context):
        max_diameter = self.parameterAsDouble(parameters, self.MAX_DIAMETER, context)
        min_duration = self.parameterAsString(parameters, self.MIN_DURATION, context)
        min_duration = pd.Timedelta(min_duration).to_pytimedelta()
        for traj in tc.trajectories:
            splits = StopSplitter(traj).split(
                max_diameter=max_diameter, min_duration=min_duration
            )
            self.tc_to_sink(splits)
            for split in splits:
                self.traj_to_sink(split)
