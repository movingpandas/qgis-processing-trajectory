import sys
from qgis.core import QgsGeometry, QgsVectorLayer

sys.path.append("..")

from qgis_processing.qgisUtils import tc_from_pt_layer


TESTDATA = "./sample_data/geolife.gpkg"
ID_COL = "trajectory_id"
TIME_COL = "t"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S+00"

def test_qgis_imports():
    polygon = QgsGeometry.fromWkt('POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))')
    result = polygon.area()
    assert result == 100

def test_dataset_availability():
    vl = QgsVectorLayer(TESTDATA, "test data")
    assert vl.isValid()

def test_tc_from_pt_layer():
    vl = QgsVectorLayer(TESTDATA, "test data")
    tc = tc_from_pt_layer(vl, TIME_COL, ID_COL, TIME_FORMAT)
    print(tc)
    assert len(tc)==5

