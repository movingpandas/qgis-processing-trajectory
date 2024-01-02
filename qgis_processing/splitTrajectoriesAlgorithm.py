# -*- coding: utf-8 -*-
import os
import sys 
import pandas as pd
from datetime import timedelta
from movingpandas import TemporalSplitter, ObservationGapSplitter

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsField, QgsFields,
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

from .qgisUtils import tc_from_pt_layer, tc_to_sink, traj_to_sink, get_pt_fields, get_traj_fields

pluginPath = os.path.dirname(__file__)


class SplitTrajectoriesAlgorithm(QgsProcessingAlgorithm):
    # script parameters
    INPUT = 'INPUT'
    TRAJ_ID_FIELD = 'OBJECT_ID_FIELD'
    TIMESTAMP_FIELD = 'TIMESTAMP_FIELD'
    OUTPUT_PTS = 'OUTPUT_PTS'
    OUTPUT_SEGS = 'OUTPUT_SEGS'
    OUTPUT_TRAJS = 'OUTPUT_TRAJS'

    def __init__(self):
        super().__init__()

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))
    
    def tr(self, text):
        return QCoreApplication.translate("split_traj", text)
    
    def group(self):
        return self.tr("Split trajectories")

    def groupId(self):
        return "split_trajectories"    

    def helpUrl(self):
        return "https://github.com/movingpandas/processing-trajectory"

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
        self.input_layer = self.parameterAsSource(parameters, self.INPUT, context)
        self.traj_id_field = self.parameterAsFields(parameters, self.TRAJ_ID_FIELD, context)[0]
        self.timestamp_field = self.parameterAsFields(parameters, self.TIMESTAMP_FIELD, context)[0]
        
        crs = self.input_layer.sourceCrs()

        self.fields_pts = get_pt_fields(self.input_layer, self.traj_id_field)
        (self.sink_pts, self.dest_pts) = self.parameterAsSink(
            parameters, self.OUTPUT_PTS, context, self.fields_pts, QgsWkbTypes.Point, crs)

        self.fields_trajs = get_traj_fields(self.input_layer, self.traj_id_field)
        (self.sink_trajs, self.dest_trajs) = self.parameterAsSink(
            parameters, self.OUTPUT_TRAJS, context, self.fields_trajs, QgsWkbTypes.LineStringM, crs)
        
        tc = tc_from_pt_layer(self.input_layer, self.timestamp_field, self.traj_id_field)#, timestamp_format)  

        self.split(tc, parameters, context)

        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}
    
    def split(self, tc, parameters, context):
        pass  # needs to be implemented by each splitter

    def postProcessAlgorithm(self, context, feedback):
        processed_layer = QgsProcessingUtils.mapLayerFromString(self.dest_pts, context)
        processed_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "pts.qml"))
        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}


class SplitObservationGapAlgorithm(SplitTrajectoriesAlgorithm):
    TIME_GAP = 'TIME_GAP'

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(QgsProcessingParameterString(
            name=self.TIME_GAP,
            description=self.tr("Time gap (timedelta, e.g. 1 hours, 15 minutes)"),
            defaultValue="1 hours",
            optional=True))
        
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
            )

    def split(self, tc, parameters, context):
        time_gap = self.parameterAsString(parameters, self.TIME_GAP, context)
        for traj in tc.trajectories:
            splits = ObservationGapSplitter(traj).split(gap=time_gap)
            tc_to_sink(splits, self.sink_pts, self.fields_pts, self.timestamp_field)
            for split in splits:
                traj_to_sink(split, self.sink_trajs)


class SplitTemporallyAlgorithm(SplitTrajectoriesAlgorithm):
    SPLIT_MODE = 'SPLIT_MODE'
    SPLIT_MODE_OPTIONS = ["year", "month", "day", "hour", ]

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(QgsProcessingParameterEnum(
            name=self.SPLIT_MODE,
            description=self.tr("Splitting mode"),
            defaultValue="day",
            options=self.SPLIT_MODE_OPTIONS,
            optional=False))

    def name(self):
        return "split_temporally"

    def displayName(self):
        return self.tr("Split trajectories at time intervals")
    
    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories "
            "using regular time intervals (year, month, day, hour): </p>" 
            "<p>For more information on trajectory splitters see: " 
            "https://movingpandas.readthedocs.io/en/main/trajectorysplitter.html</p>"
            )

    def split(self, tc, parameters, context):
        split_mode = self.parameterAsInt(parameters, self.SPLIT_MODE, context)
        split_mode = self.SPLIT_MODE_OPTIONS[split_mode]
        for traj in tc.trajectories:
            splits = TemporalSplitter(traj).split(mode=split_mode)
            tc_to_sink(splits, self.sink_pts, self.fields_pts, self.timestamp_field)
            for split in splits:
                traj_to_sink(split, self.sink_trajs)    
       

