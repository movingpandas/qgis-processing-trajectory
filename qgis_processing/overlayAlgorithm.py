import sys

import shapely.wkt
from shapely.geometry import Polygon

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProcessingParameterExtent,
    QgsProcessingParameterVectorLayer,
    QgsWkbTypes,
    QgsField,
)

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm


class OverlayTrajectoriesAlgorithm(TrajectoryManipulationAlgorithm):
    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Trajectory overlay")

    def groupId(self):
        return "TrajectoryOverlay"


class ClipTrajectoriesByExtentAlgorithm(OverlayTrajectoriesAlgorithm):
    EXTENT = "EXTENT"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterExtent(
                name=self.EXTENT, description=self.tr("Extent"), optional=False
            )
        )

    def name(self):
        return "clip_traj_extent"

    def displayName(self):
        return self.tr("Clip trajectories by extent")

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a trajectory point layers with speed and direction information "
            "as well as a trajectory line layer clipped by the specified extent.</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def helpUrl(self):
        return "https://movingpandas.org/units"

    def processTc(self, tc, parameters, context):
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        extent = shapely.wkt.loads(extent.asWktPolygon())
        clipped = tc.clip(extent)
        self.tc_to_sink(clipped)
        for traj in clipped:
            self.traj_to_sink(traj)


class ClipTrajectoriesByPolygonLayerAlgorithm(OverlayTrajectoriesAlgorithm):
    OVERLAY_LAYER = "OVERLAY_LAYER"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.OVERLAY_LAYER,
                description=self.tr("Overlay layer"),
                optional=False,
            )
        )

    def name(self):
        return "clip_traj_vector"

    def displayName(self):
        return self.tr("Clip trajectories by polygon layer")

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a trajectory point layers with speed and direction information "
            "as well as a trajectory line layer clipped by the specified vector layer.</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def helpUrl(self):
        return "https://movingpandas.org/units"

    def processTc(self, tc, parameters, context):
        vlayer = self.parameterAsVectorLayer(parameters, self.OVERLAY_LAYER, context)
        for feature in vlayer.getFeatures():
            shapely_feature = shapely.wkt.loads(feature.geometry().asWkt())
            clipped = tc.clip(shapely_feature)
            self.tc_to_sink(clipped)
            for traj in clipped:
                self.traj_to_sink(traj)


class IntersectWithPolygonLayerAlgorithm(OverlayTrajectoriesAlgorithm):
    OVERLAY_LAYER = "OVERLAY_LAYER"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.OVERLAY_LAYER,
                description=self.tr("Overlay layer"),
                optional=False,
            )
        )

    def name(self):
        return "intersect_traj_vector"

    def displayName(self):
        return self.tr("Intersect trajectories with polygon layer")

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a trajectory point layers with speed and direction information "
            "as well as a trajectory line layer which ihntersects the specified vector layer.</p>"
            "<p><b>Speed</b> is calculated based on the input layer CRS information and "
            "converted to the desired speed units. For more info on the supported units, "
            "see https://movingpandas.org/units</p>"
            "<p><b>Direction</b> is calculated between consecutive locations. Direction "
            "values are in degrees, starting North turning clockwise.</p>"
        )

    def helpUrl(self):
        return "https://movingpandas.org/units"

    def setup_pt_sink(self, parameters, context, tc, crs):        
        self.fields_pts = self.get_pt_fields(
            [
                QgsField(tc.get_speed_col(), QVariant.Double),
                QgsField(tc.get_direction_col(), QVariant.Double),
            ],
        )

        vlayer = self.parameterAsVectorLayer(parameters, self.OVERLAY_LAYER, context)
        for field in vlayer.fields():
            field.setName(f'intersecting_{field.name()}')
            self.fields_pts.append(field)

        (self.sink_pts, self.dest_pts) = self.parameterAsSink(
            parameters,
            self.OUTPUT_PTS,
            context,
            self.fields_pts,
            QgsWkbTypes.Point,
            crs,
        )

    def setup_traj_sink(self, parameters, context, crs):
        self.fields_trajs = self.get_traj_fields()
        
        vlayer = self.parameterAsVectorLayer(parameters, self.OVERLAY_LAYER, context)
        for field in vlayer.fields():
            field.setName(f'intersecting_{field.name()}')
            self.fields_trajs.append(field)

        (self.sink_trajs, self.dest_trajs) = self.parameterAsSink(
            parameters,
            self.OUTPUT_TRAJS,
            context,
            self.fields_trajs,
            QgsWkbTypes.LineStringM,
            crs,
        )

    def processTc(self, tc, parameters, context):
        vlayer = self.parameterAsVectorLayer(parameters, self.OVERLAY_LAYER, context)
        layer_fields = vlayer.fields()
        field_names = [field.name() for field in layer_fields]
        field_names_to_add = [f'intersecting_{name}' for name in field_names]

        for feature in vlayer.getFeatures():
            attrs = feature.attributes()

            shapely_feature = {
                "geometry": shapely.wkt.loads(feature.geometry().asWkt()),
                "properties": dict(zip(field_names, attrs)),
            }
            intersecting = tc.intersection(shapely_feature)

            self.tc_to_sink(intersecting, field_names_to_add=field_names_to_add)
            for traj in intersecting:
                self.traj_to_sink(traj, attr_first_to_add=field_names_to_add)
