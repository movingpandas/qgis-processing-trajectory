import sys
import pandas as pd
from pyproj import CRS
from movingpandas import TrajectoryCollection
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFeatureSink,
    QgsMessageLog,
    Qgis,
)
from qgis.PyQt.QtCore import QDateTime


def trajectories_from_qgis_point_layer(
    layer, time_field_name, trajectory_id_field, time_format
):
    # TODO: remove
    return tc_from_pt_layer(layer, time_field_name, trajectory_id_field, time_format)


def df_from_pt_layer(layer, time_field_name, trajectory_id_field):
    names = [field.name() for field in layer.fields()]
    data = []
    for feature in layer.getFeatures():
        my_dict = {}
        for i, a in enumerate(feature.attributes()):
            # QgsMessageLog.logMessage(f"{names[i]} | {time_field_name}", "Trajectools", level=Qgis.Info )
            if names[i] == time_field_name:  # and type(a) == "QDateTime":
                try:
                    a = a.toPyDateTime()
                except:
                    pass
            my_dict[names[i]] = a
        pt = feature.geometry().asPoint()
        my_dict["geom_x"] = pt.x()
        my_dict["geom_y"] = pt.y()
        data.append(my_dict)
    df = pd.DataFrame(data)
    return df


def tc_from_pt_layer(layer, time_field_name, trajectory_id_field):
    df = df_from_pt_layer(layer, time_field_name, trajectory_id_field)
    crs = CRS(int(layer.sourceCrs().geographicCrsAuthId().split(":")[1]))
    return tc_from_df(df, time_field_name, trajectory_id_field, crs)


def tc_from_df(df, time_field_name, trajectory_id_field, crs):
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
    values = row.values.tolist()[:-1]
    # for v in values:
    #    QgsMessageLog.logMessage(str(type(v)), "Trajectools", level=Qgis.Info )
    f.setAttributes(values)
    return f
