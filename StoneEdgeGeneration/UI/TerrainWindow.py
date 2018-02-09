import sys 
import bpy
from importlib import reload

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets

from StoneEdgeGeneration import utils, UI
from StoneEdgeGeneration.UI import BaseWindow, Parameter
reload(utils)
reload(UI)
reload(Parameter)
reload(BaseWindow)

class TerrainWindow(BaseWindow.BaseWindow):
    def __init__(self):
        super(TerrainWindow, self).__init__()
        self.setWindowTitle("Terrain Generation")