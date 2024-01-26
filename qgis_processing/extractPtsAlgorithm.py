import sys

import shapely.wkt
from shapely.geometry import Polygon

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessingParameterExtent,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSink,
    QgsProcessing,
    QgsWkbTypes,
    QgsField,
    QgsFeatureSink,
    QgsFields,
)
from qgis.core import QgsMessageLog, Qgis

import pandas as pd
from movingpandas import TrajectoryStopDetector

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoriesAlgorithm
from .qgisUtils import feature_from_gdf_row


class ExtractODPtsAlgorithm(TrajectoriesAlgorithm):
    ORIGIN_PTS = "ORIGIN_PTS"
    DESTINATIONS_PTS = "DESTINATIONS_PTS"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.ORIGIN_PTS,
                description=self.tr("Origin points"),
                type=QgsProcessing.TypeVectorPoint,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.DESTINATIONS_PTS,
                description=self.tr("Destination points"),
                type=QgsProcessing.TypeVectorPoint,
            )
        )

    def group(self):
        return self.tr("Basic")

    def groupId(self):
        return "TrajectoryBasic"

    def name(self):
        return "extract_od_pts"

    def displayName(self):
        return self.tr("Extract OD points")

    def shortHelpString(self):
        return self.tr("<p>Extracts start and/or end points of trajectories.</p>")

    def processAlgorithm(self, parameters, context, feedback):
        tc, crs = self.create_tc(parameters, context)

        self.fields_pts = self.get_pt_fields(
            [
                QgsField(tc.get_speed_col(), QVariant.Double),
                QgsField(tc.get_direction_col(), QVariant.Double),
            ],
        )
        (self.sink_orig, self.orig_pts) = self.parameterAsSink(
            parameters,
            self.ORIGIN_PTS,
            context,
            self.fields_pts,
            QgsWkbTypes.Point,
            crs,
        )
        (self.sink_dest, self.dest_pts) = self.parameterAsSink(
            parameters,
            self.DESTINATIONS_PTS,
            context,
            self.fields_pts,
            QgsWkbTypes.Point,
            crs,
        )

        self.processTc(tc, parameters, context)

        return {self.ORIGIN_PTS: self.orig_pts, self.DESTINATIONS_PTS: self.dest_pts}

    def processTc(self, tc, parameters, context):
        try:
            gdf = tc.get_start_locations()
        except ValueError:  # when the tc is empty
            return
        gdf = gdf.convert_dtypes()
        gdf[self.timestamp_field] = gdf[self.timestamp_field].astype(str)
        names = [field.name() for field in self.fields_pts]
        names.append("geometry")
        gdf = gdf[names]
        # QgsMessageLog.logMessage(str(gdf), "Trajectools", level=Qgis.Info )

        for _, row in gdf.iterrows():
            f = feature_from_gdf_row(row)
            self.sink_orig.addFeature(f, QgsFeatureSink.FastInsert)

        gdf = tc.get_end_locations()
        gdf = gdf.convert_dtypes()
        gdf[self.timestamp_field] = gdf[self.timestamp_field].astype(str)
        gdf = gdf[names]

        for _, row in gdf.iterrows():
            f = feature_from_gdf_row(row)
            self.sink_dest.addFeature(f, QgsFeatureSink.FastInsert)


class ExtractStopsAlgorithm(TrajectoriesAlgorithm):
    MAX_DIAMETER = "MAX_DIAMETER"
    MIN_DURATION = "MIN_DURATION"
    STOP_PTS = "STOP_PTS"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.MAX_DIAMETER,
                description=self.tr("Max stop diameter (meters)"),
                defaultValue=30,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.MIN_DURATION,
                description=self.tr(
                    "Min stop duration (timedelta, e.g. 1 hours, 15 minutes)"
                ),
                defaultValue="2 minutes",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.STOP_PTS,
                description=self.tr("Stop points"),
                type=QgsProcessing.TypeVectorPoint,
            )
        )

    def group(self):
        return self.tr("Basic")

    def groupId(self):
        return "TrajectoryBasic"

    def name(self):
        return "extract_stop_pts"

    def displayName(self):
        return self.tr("Extract stop points")

    def shortHelpString(self):
        return self.tr("<p>Extracts stop points from trajectories.</p>")

    def processAlgorithm(self, parameters, context, feedback):
        tc, crs = self.create_tc(parameters, context)

        self.fields_pts = QgsFields()
        self.fields_pts.append(QgsField("stop_id", QVariant.String))
        self.fields_pts.append(QgsField("start_time", QVariant.String))  # .DateTime))
        self.fields_pts.append(QgsField("end_time", QVariant.String))  # .DateTime))
        self.fields_pts.append(QgsField("traj_id", QVariant.String))
        self.fields_pts.append(QgsField("duration_s", QVariant.Double))

        (self.sink, self.stop_pts) = self.parameterAsSink(
            parameters,
            self.STOP_PTS,
            context,
            self.fields_pts,
            QgsWkbTypes.Point,
            crs,
        )

        self.processTc(tc, parameters, context)

        return {self.STOP_PTS: self.stop_pts}

    def processTc(self, tc, parameters, context):
        max_diameter = self.parameterAsDouble(parameters, self.MAX_DIAMETER, context)
        min_duration = self.parameterAsString(parameters, self.MIN_DURATION, context)
        min_duration = pd.Timedelta(min_duration).to_pytimedelta()

        gdf = TrajectoryStopDetector(tc).get_stop_points(
            max_diameter=max_diameter, min_duration=min_duration
        )
        gdf = gdf.convert_dtypes()
        gdf["stop_id"] = gdf.index.astype(str)
        gdf["start_time"] = gdf["start_time"].astype(str)
        gdf["end_time"] = gdf["end_time"].astype(str)

        names = [field.name() for field in self.fields_pts]
        names.append("geometry")
        gdf = gdf[names]

        for _, row in gdf.iterrows():
            f = feature_from_gdf_row(row)
            self.sink.addFeature(f, QgsFeatureSink.FastInsert)
