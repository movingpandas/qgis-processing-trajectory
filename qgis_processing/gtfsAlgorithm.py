import os
import sys

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFile,
    QgsProcessingParameterField,
    QgsProcessingUtils,
    QgsCoordinateReferenceSystem,
    QgsWkbTypes,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsGeometry,
    QgsFeatureSink,
)

try:
    from gtfs_functions import Feed
except ImportError as error:
    raise ImportError(
        "Missing optional dependencies. To use the GTFS algorithms please "
        "install gtfs_functions. For details see: "
        "https://github.com/Bondify/gtfs_functions."
    ) from error

sys.path.append("..")

from .qgisUtils import tc_from_pt_layer, feature_from_gdf_row, df_from_pt_layer

pluginPath = os.path.dirname(__file__)


class GtfsStopsAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"  

    def __init__(self):
        super().__init__()

    def name(self):
        return "gtfs_stops"

    def displayName(self):
        return self.tr("Extract stops")

    def group(self):
        return self.tr("GTFS")

    def groupId(self):
        return "Gtfs"

    def tr(self, text):
        return QCoreApplication.translate("trajectools", text)

    def helpUrl(self):
        return "https://github.com/Bondify/gtfs_functions"

    def shortHelpString(self):
        return self.tr(
            "<p>Extracts stops from a GTFS ZIP file using "
            "gtfs_functions.Feed.stops</p>"
        )

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr("Input GTFS file"),
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT,
                description=self.tr("GTFS stops"),
                type=QgsProcessing.TypeVectorPoint,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        gtfs_file = self.parameterAsFile(parameters, self.INPUT, context)
        (self.sink_stops, self.dest_stops) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            self.get_fields(),
            QgsWkbTypes.Point,
            QgsCoordinateReferenceSystem("EPSG:4326"),
        )

        feed = Feed(gtfs_file)
        stops = feed.stops
        for _, stop in stops.iterrows():
            pt = QgsGeometry.fromWkt(stop.geometry.wkt)
            f = QgsFeature()
            f.setGeometry(pt)
            attrs = [
                stop.stop_id,
                stop.stop_code,
                stop.stop_name
            ]
            f.setAttributes(attrs)
            self.sink_stops.addFeature(f, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: self.dest_stops}

    def get_fields(self):
        fields = QgsFields()
        fields.append(QgsField("stop_id", QVariant.String))
        fields.append(QgsField("stop_code", QVariant.String))
        fields.append(QgsField("stop_name", QVariant.String))
        return fields


class GtfsShapesAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    SPEED_OPTION = "SPEED"
    OUTPUT = "OUTPUT"

    def __init__(self):
        super().__init__()

    def name(self):
        return "gtfs_shapes"

    def displayName(self):
        return self.tr("Extract shapes")

    def group(self):
        return self.tr("GTFS")

    def groupId(self):
        return "Gtfs"

    def tr(self, text):
        return QCoreApplication.translate("trajectools", text)

    def helpUrl(self):
        return "https://github.com/Bondify/gtfs_functions"

    def shortHelpString(self):
        return self.tr(
            "<p>Extracts shapes from a GTFS ZIP file using "
            "gtfs_functions.Feed.shapes</p>"
        )

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr("Input GTFS file"),
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT,
                description=self.tr("GTFS shapes"),
                type=QgsProcessing.TypeVectorLine,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        gtfs_file = self.parameterAsFile(parameters, self.INPUT, context)
        (self.sink_shapes, self.dest_shapes) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            self.get_fields(),
            QgsWkbTypes.LineStringM,
            QgsCoordinateReferenceSystem("EPSG:4326"),
        )

        feed = Feed(gtfs_file)
        segments = feed.shapes
        for _, shape in segments.iterrows():
            line = QgsGeometry.fromWkt(shape.geometry.wkt)
            f = QgsFeature()
            f.setGeometry(line)
            attrs = [
                shape.shape_id
            ]
            f.setAttributes(attrs)
            self.sink_shapes.addFeature(f, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: self.dest_shapes}

    def get_fields(self):
        fields = QgsFields()
        fields.append(QgsField("shape_id", QVariant.String))
        return fields


class GtfsSegmentsAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    SPEED_OPTION = "SPEED"
    OUTPUT = "OUTPUT"

    def __init__(self):
        super().__init__()

    def name(self):
        return "gtfs_segments"

    def displayName(self):
        return self.tr("Extract segments")

    def group(self):
        return self.tr("GTFS")

    def groupId(self):
        return "Gtfs"

    def tr(self, text):
        return QCoreApplication.translate("trajectools", text)

    def helpUrl(self):
        return "https://github.com/Bondify/gtfs_functions"

    def shortHelpString(self):
        return self.tr(
            "<p>Extracts segments from a GTFS ZIP file using "
            "gtfs_functions.Feed.segments</p>"
            "<p>Optionally adds scheduled average speeds using"
            "gtfs_functions.Feed.avg_speeds</p>"
        )

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT,
                description=self.tr("Input GTFS file"),
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.SPEED_OPTION,
                description=self.tr("Add scheduled speeds"),
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT,
                description=self.tr("GTFS segments"),
                type=QgsProcessing.TypeVectorLine,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        gtfs_file = self.parameterAsFile(parameters, self.INPUT, context)
        add_avg_speed = self.parameterAsBool(parameters, self.SPEED_OPTION, context)
        (self.sink_segments, self.dest_segments) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            self.get_fields(add_avg_speed),
            QgsWkbTypes.LineStringM,
            QgsCoordinateReferenceSystem("EPSG:4326"),
        )

        feed = Feed(gtfs_file)
        segments = self.get_segments(feed, add_avg_speed)
        for _, segment in segments.iterrows():
            line = QgsGeometry.fromWkt(segment.geometry.wkt)
            f = QgsFeature()
            f.setGeometry(line)
            attrs = [
                segment.shape_id,
                segment.route_id,
                segment.route_name,
                segment.direction_id,
                segment.stop_sequence,
                segment.segment_name,
                segment.start_stop_name,
                segment.end_stop_name,
                segment.segment_id,
                segment.start_stop_id,
                segment.end_stop_id,
                segment.distance_m,
            ]
            if add_avg_speed:
                attrs = attrs + [
                    segment.window,
                    segment.speed_kmh,
                    segment.avg_route_speed_kmh,
                    segment.segment_max_speed_kmh,
                    segment.runtime_sec,
                ]
            f.setAttributes(attrs)
            self.sink_segments.addFeature(f, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: self.dest_segments}

    def get_segments(self, feed, add_avg_speed=False):
        if add_avg_speed:
            segments = feed.avg_speeds
        else:
            segments = feed.segments
        return segments

    def get_fields(self, add_avg_speed):
        fields = QgsFields()
        fields.append(QgsField("shape_id", QVariant.String))
        fields.append(QgsField("route_id", QVariant.String))
        fields.append(QgsField("route_name", QVariant.String))
        fields.append(QgsField("direction_id", QVariant.String))
        fields.append(QgsField("stop_sequence", QVariant.Int))
        fields.append(QgsField("segment_name", QVariant.String))
        fields.append(QgsField("start_stop_name", QVariant.String))
        fields.append(QgsField("end_stop_name", QVariant.String))
        fields.append(QgsField("segment_id", QVariant.String))
        fields.append(QgsField("start_stop_id", QVariant.String))
        fields.append(QgsField("end_stop_id", QVariant.String))
        fields.append(QgsField("distance_m", QVariant.Double))
        if add_avg_speed:
            fields.append(QgsField("window", QVariant.String))
            fields.append(QgsField("speed_kmh", QVariant.Double))
            fields.append(QgsField("avg_route_speed_kmh", QVariant.Double))
            fields.append(QgsField("segment_max_speed_kmh", QVariant.Double))
            fields.append(QgsField("runtime_sec", QVariant.Double))
        return fields
