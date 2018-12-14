# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectoriesFromPointLayer.py
    ---------------------
    Date                 : December 2018
    Copyright            : (C) 2018 by Anita Graser
    Email                : anitagraser@gmx.at
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os
import sys 

import pandas as pd 
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate
from datetime import datetime, timedelta


from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon

from qgis.core import (QgsField,QgsFields,
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
                       QgsWkbTypes
                      )

sys.path.append("..")
from processing_trajectory.trajectory import Trajectory
from .qgisUtils import trajectories_from_qgis_point_layer

pluginPath = os.path.dirname(__file__)


class TrajectoriesFromPointLayerAlgorithm(QgsProcessingAlgorithm):
    # script parameters
    INPUT = 'INPUT'
    TRAJ_ID_FIELD = 'OBJECT_ID_FIELD'
    TIMESTAMP_FIELD = 'TIMESTAMP_FIELD'
    TIMESTAMP_FORMAT = 'TIMESTAMP_FORMAT'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def name(self):
        return "traj_from_point_layer"

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))

    def tr(self, text):
        return QCoreApplication.translate("clip_traj_extent", text)

    def displayName(self):
        return self.tr("Trajectories from point layer")

    def group(self):
        return self.tr("Basic")

    def groupId(self):
        return "TrajectoryBasic"

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a LineStringM layer from points grouped by trajectory ID field, " + 
            "ordered by time.</p><p>Temporal information " + 
            "is stored as unixtime in the m value.</p>")

    def helpUrl(self):
        return "https://github.com/anitagraser/processing-trajectory"

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
        # output layer
        self.addParameter(QgsProcessingParameterFeatureSink(
            name=self.OUTPUT,
            description=self.tr("Trajectories"),
            type=QgsProcessing.TypeVectorLine))

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsSource(parameters, self.INPUT, context)
        traj_id_field = self.parameterAsFields(parameters, self.TRAJ_ID_FIELD, context)[0]
        timestamp_field = self.parameterAsFields(parameters, self.TIMESTAMP_FIELD, context)[0]
        timestamp_format = self.parameterAsString(parameters, self.TIMESTAMP_FORMAT, context)
        
        output_fields = QgsFields()
        output_fields.append(QgsField(traj_id_field, QVariant.String))
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               output_fields, 
                                               QgsWkbTypes.LineStringM, 
                                               input_layer.sourceCrs())
        
        trajectories = trajectories_from_qgis_point_layer(input_layer, timestamp_field, traj_id_field, timestamp_format)
        
        for traj in trajectories:
            line = QgsGeometry.fromWkt(traj.to_linestringm_wkt())
            f = QgsFeature()
            f.setGeometry(line)
            f.setAttributes([traj.id])
            sink.addFeature(f, QgsFeatureSink.FastInsert)
        
        # default return type for function
        return {self.OUTPUT: dest_id}
