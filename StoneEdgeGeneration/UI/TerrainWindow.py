from importlib import reload

from StoneEdgeGeneration import utils, UI
from StoneEdgeGeneration.UI import BaseWindow
reload(utils)
reload(UI)
reload(BaseWindow)


class TerrainWindow(BaseWindow.BaseWindow):
    def __init__(self):
        super(TerrainWindow, self).__init__()
        self.setWindowTitle("Terrain Generation")
