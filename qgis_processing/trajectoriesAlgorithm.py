import os
import sys

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingUtils,
    QgsWkbTypes,
    QgsProcessingParameterString,
    QgsField,
    QgsFields,
)

sys.path.append("..")

from .qgisUtils import tc_from_pt_layer

pluginPath = os.path.dirname(__file__)


class TrajectoriesAlgorithm(QgsProcessingAlgorithm):
    # script parameters
    INPUT = "INPUT"
    TRAJ_ID_FIELD = "OBJECT_ID_FIELD"
    TIMESTAMP_FIELD = "TIMESTAMP_FIELD"
    OUTPUT_PTS = "OUTPUT_PTS"
    OUTPUT_SEGS = "OUTPUT_SEGS"
    OUTPUT_TRAJS = "OUTPUT_TRAJS"
    SPEED_UNIT = "SPEED_UNIT"

    def __init__(self):
        super().__init__()

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))

    def tr(self, text):
        return QCoreApplication.translate("split_traj", text)

    def helpUrl(self):
        return "https://github.com/movingpandas/processing-trajectory"

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        # input layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                name=self.INPUT,
                description=self.tr("Input point layer"),
                types=[QgsProcessing.TypeVectorPoint],
            )
        )
        # fields
        self.addParameter(
            QgsProcessingParameterField(
                name=self.TRAJ_ID_FIELD,
                description=self.tr("Trajectory ID field"),
                defaultValue="trajectory_id",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                allowMultiple=False,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.TIMESTAMP_FIELD,
                description=self.tr("Timestamp field"),
                defaultValue="t",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                allowMultiple=False,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.SPEED_UNIT,
                description=self.tr("Speed units (e.g. km/h, m/s)"),
                defaultValue="km/h",
                optional=False,
            )
        )
        # output layer
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT_PTS,
                description=self.tr("Trajectory points"),
                type=QgsProcessing.TypeVectorPoint,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT_TRAJS,
                description=self.tr("Trajectories"),
                type=QgsProcessing.TypeVectorLine,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        self.input_layer = self.parameterAsSource(parameters, self.INPUT, context)
        self.traj_id_field = self.parameterAsFields(
            parameters, self.TRAJ_ID_FIELD, context
        )[0]
        self.timestamp_field = self.parameterAsFields(
            parameters, self.TIMESTAMP_FIELD, context
        )[0]
        speed_units = self.parameterAsString(
            parameters, self.SPEED_UNIT, context
        ).split("/")
        crs = self.input_layer.sourceCrs()

        tc = tc_from_pt_layer(
            self.input_layer, self.timestamp_field, self.traj_id_field
        )
        tc.add_speed(units=tuple(speed_units), overwrite=True)
        tc.add_direction(overwrite=True)

        self.fields_pts = self.get_pt_fields(
            [
                QgsField(tc.get_speed_col(), QVariant.Double),
                QgsField(tc.get_direction_col(), QVariant.Double),
            ],
        )
        (self.sink_pts, self.dest_pts) = self.parameterAsSink(
            parameters,
            self.OUTPUT_PTS,
            context,
            self.fields_pts,
            QgsWkbTypes.Point,
            crs,
        )

        self.fields_trajs = self.get_traj_fields()
        (self.sink_trajs, self.dest_trajs) = self.parameterAsSink(
            parameters,
            self.OUTPUT_TRAJS,
            context,
            self.fields_trajs,
            QgsWkbTypes.LineStringM,
            crs,
        )

        self.processTc(tc, parameters, context)

        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}

    def processTc(self, tc, parameters, context):
        pass  # needs to be implemented by each splitter

    def postProcessAlgorithm(self, context, feedback):
        pts_layer = QgsProcessingUtils.mapLayerFromString(self.dest_pts, context)
        pts_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "pts.qml"))
        traj_layer = QgsProcessingUtils.mapLayerFromString(self.dest_trajs, context)
        traj_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "traj.qml"))
        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}

    def get_pt_fields(self, fields_to_add=[]):
        fields = QgsFields()
        for field in self.input_layer.fields():
            if field.name() == "fid":
                continue
            elif field.name() == self.traj_id_field:
                # we need to make sure the ID field is String
                fields.append(QgsField(self.traj_id_field, QVariant.String))
            else:
                fields.append(field)
        for field in fields_to_add:
            i = fields.indexFromName(field.name())
            if i < 0:
                fields.append(field)
        return fields

    def get_traj_fields(self):
        fields = QgsFields()
        fields.append(QgsField(self.traj_id_field, QVariant.String))
        return fields
