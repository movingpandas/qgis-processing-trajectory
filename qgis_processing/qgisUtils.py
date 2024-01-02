import sys
import pandas as pd
from geopandas import GeoDataFrame
from PyQt5 import QtCore
from shapely.geometry import Point
from datetime import datetime
from pyproj import CRS

sys.path.append("..")

from movingpandas import TrajectoryCollection
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFeatureSink,
    QgsFields,
    QgsField,
)
from qgis.PyQt.QtCore import QVariant


def trajectories_from_qgis_point_layer(
    layer, time_field_name, trajectory_id_field, time_format
):
    # TODO: remove
    return tc_from_pt_layer(layer, time_field_name, trajectory_id_field, time_format)


def tc_from_pt_layer(layer, time_field_name, trajectory_id_field):
    names = [field.name() for field in layer.fields()]
    data = []
    for feature in layer.getFeatures():
        my_dict = {}
        for i, a in enumerate(feature.attributes()):
            my_dict[names[i]] = a
        pt = feature.geometry().asPoint()
        my_dict["geom_x"] = pt.x()
        my_dict["geom_y"] = pt.y()
        data.append(my_dict)
    df = pd.DataFrame(data)
    crs = CRS(int(layer.sourceCrs().geographicCrsAuthId().split(":")[1]))
    tc = TrajectoryCollection(
        df,
        traj_id_col=trajectory_id_field,
        x="geom_x",
        y="geom_y",
        t=time_field_name,
        crs=crs,
    )
    return tc


def feature_from_gdf_row(row):
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(row.geometry.x, row.geometry.y)))
    f.setAttributes(row.values.tolist()[:-1])
    return f


def tc_to_sink(tc, sink, fields, timestamp_field):
    gdf = tc.to_point_gdf()
    gdf[timestamp_field] = gdf.index.astype(str)
    names = [field.name() for field in fields]
    names.append("geometry")
    gdf = gdf[names]

    for _, row in gdf.iterrows():
        f = feature_from_gdf_row(row)
        sink.addFeature(f, QgsFeatureSink.FastInsert)


def traj_to_sink(traj, sink):
    line = QgsGeometry.fromWkt(traj.to_linestringm_wkt())
    f = QgsFeature()
    f.setGeometry(line)
    f.setAttributes([traj.id])
    sink.addFeature(f, QgsFeatureSink.FastInsert)
