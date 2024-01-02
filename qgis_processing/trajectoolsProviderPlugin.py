import sys

from qgis.core import QgsApplication

sys.path.append("..")

from .trajectoolsProvider import TrajectoolsProvider


class TrajectoryProviderPlugin:
    def __init__(self):
        self.provider = TrajectoolsProvider()

    def initGui(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
