import os
import sys

from pandas import merge
from pyproj import CRS
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import QgsWkbTypes, QgsField, QgsProcessingUtils

try:
    from skmob.privacy import attacks
    from skmob.core.trajectorydataframe import TrajDataFrame
except ImportError as error:
    raise ImportError(
        "Missing optional dependencies. To use the privacy attacks please "
        "install scikit-mobility "
        "(see https://github.com/scikit-mobility/scikit-mobility)."
    ) from error

sys.path.append("..")

from .qgisUtils import tc_from_df
from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm

pluginPath = os.path.dirname(__file__)


class HomeWorkAttack(TrajectoryManipulationAlgorithm):
    def __init__(self):
        super().__init__()

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "skmob.png"))

    def name(self):
        return "home_work_attack"

    def displayName(self):
        return self.tr("Home and work attack")

    def group(self):
        return self.tr("Privacy")

    def groupId(self):
        return "TrajectoryPrivacy"

    def shortHelpString(self):
        return self.tr(
            "<p>In a home and work attack the adversary knows the "
            "coordinates of the two locations most frequently visited "
            "by an individual, and matches them against frequency "
            "vectors. A frequency vector is an aggregation on trajectory "
            "data showing the unique locations visited by an individual "
            "and the frequency with which he visited those locations. "
        )

    def helpUrl(self):
        return "https://scikit-mobility.github.io/scikit-mobility/reference/privacy.html#skmob.privacy.attacks.HomeWorkAttack"

    def createInstance(self):
        return type(self)()

    def processAlgorithm(self, parameters, context, feedback):
        df = self.create_df(parameters, context)
        df_copy = df.drop(
            columns=["lng", "lat"]
        )  # skmob may throw an error if these columns exist
        tdf = TrajDataFrame(
            df_copy,
            longitude="geom_x",
            latitude="geom_y",
            datetime=self.timestamp_field,
            user_id=self.traj_id_field,
        )
        at = attacks.HomeWorkAttack()
        r = at.assess_risk(tdf)
        df = merge(r, df, on="uid")

        crs = self.input_layer.sourceCrs()
        crs_no = CRS(int(crs.geographicCrsAuthId().split(":")[1]))
        tc = tc_from_df(df, self.timestamp_field, self.traj_id_field, crs_no)
        tc.add_speed(units=tuple(self.speed_units), overwrite=True)
        tc.add_direction(overwrite=True)

        self.fields_pts = self.get_pt_fields(
            [
                QgsField(tc.get_speed_col(), QVariant.Double),
                QgsField(tc.get_direction_col(), QVariant.Double),
                QgsField("risk", QVariant.Double),
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

        self.fields_trajs = self.get_traj_fields([QgsField("risk", QVariant.Double)])
        (self.sink_trajs, self.dest_trajs) = self.parameterAsSink(
            parameters,
            self.OUTPUT_TRAJS,
            context,
            self.fields_trajs,
            QgsWkbTypes.LineStringM,
            crs,
        )

        self.processTc(tc)

        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}

    def processTc(self, tc):
        self.tc_to_sink(tc)
        for traj in tc.trajectories:
            self.traj_to_sink(traj, attr_mean_to_add=["risk"])

    def postProcessAlgorithm(self, context, feedback):
        pts_layer = QgsProcessingUtils.mapLayerFromString(self.dest_pts, context)
        pts_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "pts.qml"))
        traj_layer = QgsProcessingUtils.mapLayerFromString(self.dest_trajs, context)
        traj_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "risk.qml"))
        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}
