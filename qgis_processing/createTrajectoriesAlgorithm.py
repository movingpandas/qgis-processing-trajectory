# -*- coding: utf-8 -*-
import os
import sys 

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon

from qgis.core import (QgsField, QgsFields, QgsPointXY, 
                       QgsGeometry,
                       QgsFeature,
                       QgsFeatureSink,
                       QgsFeatureRequest,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsWkbTypes,
                       QgsProcessingUtils
                      )

sys.path.append("..")

from .qgisUtils import tc_from_pt_layer, tc_to_sink

pluginPath = os.path.dirname(__file__)


class CreateTrajectoriesAlgorithm(QgsProcessingAlgorithm):
    # script parameters
    INPUT = 'INPUT'
    TRAJ_ID_FIELD = 'OBJECT_ID_FIELD'
    TIMESTAMP_FIELD = 'TIMESTAMP_FIELD'
    TIMESTAMP_FORMAT = 'TIMESTAMP_FORMAT'
    OUTPUT_PTS = 'OUTPUT_PTS'
    OUTPUT_SEGS = 'OUTPUT_SEGS'
    OUTPUT_TRAJS = 'OUTPUT_TRAJS'
    SPEED_UNIT = 'SPEED_UNIT'

    def __init__(self):
        super().__init__()

    def name(self):
        return "create_trajectory"

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))

    def tr(self, text):
        return QCoreApplication.translate("create_trajectory", text)

    def displayName(self):
        return self.tr("Create trajectories")

    #def group(self):
    #    return self.tr("Basic")

    #def groupId(self):
    #    return "TrajectoryBasic"

    def shortHelpString(self):
        return self.tr(
            "<p><b>Speed</b> is calculated based on the input layer CRS information and " + 
            "converted to the desired speed units. For more info on the supported units, " +
            "see https://movingpandas.org/units </p>" +
            "<p><b>Direction</b> is calculated between consecutive locations. Direction " +
            "values are in degrees, starting North turning clockwise.</p>"
            )

    def helpUrl(self):
        return "https://movingpandas.org/units"

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        # input layer
        self.addParameter(QgsProcessingParameterFeatureSource(
            name=self.INPUT,
            description=self.tr("Input point layer"),
            types=[QgsProcessing.TypeVectorPoint]))
        # fields
        self.addParameter(QgsProcessingParameterField(
            name=self.TRAJ_ID_FIELD,
            description=self.tr("Trajectory ID field"),
            defaultValue="trajectory_id",
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.Any,
            allowMultiple=False,
            optional=False))
        self.addParameter(QgsProcessingParameterField(
            name=self.TIMESTAMP_FIELD,
            description=self.tr("Timestamp field"),
            defaultValue="t",
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.Any,
            allowMultiple=False,
            optional=False))
        self.addParameter(QgsProcessingParameterString(
            name=self.TIMESTAMP_FORMAT,
            description=self.tr("Timestamp format"),
            defaultValue="%Y-%m-%d %H:%M:%S+00",
            optional=False))
        self.addParameter(QgsProcessingParameterString(
            name=self.SPEED_UNIT,
            description=self.tr("Speed units (e.g. km/h, m/s)"),
            defaultValue="km/h",
            optional=False))
        # output layer
        self.addParameter(QgsProcessingParameterFeatureSink(
            name=self.OUTPUT_PTS,
            description=self.tr("Trajectory points"),
            type=QgsProcessing.TypeVectorPoint))
        self.addParameter(QgsProcessingParameterFeatureSink(
            name=self.OUTPUT_TRAJS,
            description=self.tr("Trajectories"),
            type=QgsProcessing.TypeVectorLine))

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsSource(parameters, self.INPUT, context)
        traj_id_field = self.parameterAsFields(parameters, self.TRAJ_ID_FIELD, context)[0]
        timestamp_field = self.parameterAsFields(parameters, self.TIMESTAMP_FIELD, context)[0]
        timestamp_format = self.parameterAsString(parameters, self.TIMESTAMP_FORMAT, context)
        speed_units = self.parameterAsString(parameters, self.SPEED_UNIT, context).split("/")
        
        tc = tc_from_pt_layer(input_layer, timestamp_field, traj_id_field, timestamp_format)
        tc.add_speed(units=tuple(speed_units))
        tc.add_direction()

        self.dest_pts = self.create_points(parameters, context, input_layer, timestamp_field, tc)
        self.dest_trajs = self.create_trajectories(parameters, context, input_layer, traj_id_field, tc)        

        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}
    
    def postProcessAlgorithm(self, context, feedback):
        processed_layer = QgsProcessingUtils.mapLayerFromString(self.dest_pts, context)
        processed_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "pts.qml"))
        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}

    def create_points(self, parameters, context, input_layer, timestamp_field, tc):
        output_fields = input_layer.fields()
        self.drop_fid_field(output_fields)
        output_fields.append(QgsField(tc.get_speed_col(), QVariant.Double))
        output_fields.append(QgsField(tc.get_direction_col(), QVariant.Double))

        (sink, dest) = self.parameterAsSink(
            parameters, self.OUTPUT_PTS, context, output_fields, QgsWkbTypes.Point, input_layer.sourceCrs())

        tc_to_sink(tc, sink, output_fields, timestamp_field)
        return dest

    def drop_fid_field(self, output_fields):
        i = output_fields.indexFromName("fid")
        if i >= 0: 
            output_fields.remove(i)

    def create_trajectories(self, parameters, context, input_layer, traj_id_field, tc):
        output_fields_lines = QgsFields()
        output_fields_lines.append(QgsField(traj_id_field, QVariant.String))

        (sink, dest) = self.parameterAsSink(
            parameters, self.OUTPUT_TRAJS, context, output_fields_lines, QgsWkbTypes.LineStringM, input_layer.sourceCrs())

        for traj in tc.trajectories:
            line = QgsGeometry.fromWkt(traj.to_linestringm_wkt())
            f = QgsFeature()
            f.setGeometry(line)
            f.setAttributes([traj.id])
            sink.addFeature(f, QgsFeatureSink.FastInsert)
        return dest
    
