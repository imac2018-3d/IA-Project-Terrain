from importlib import reload
import sys 
from PyQt5 import QtWidgets, QtCore

from StoneEdgeGeneration import utils, UI, Terrain, Asset
reload(utils)
reload(UI)
reload(Terrain)
reload(Asset)

from StoneEdgeGeneration.Asset import genericgenetic

from StoneEdgeGeneration.UI import TerrainWindow, AssetWindow, Parameter, Individual
reload(TerrainWindow)
reload(AssetWindow)
reload(Parameter)
reload(Individual)

def loadAsset():
    return AssetWindow.AssetWindow()

def loadTerrain():
    window = TerrainWindow.TerrainWindow()
    
    # EXAMPLE OF SLIDER PARAMETER
    nbGeneration = Parameter.SliderParameter("Number of generations", 15, 10, 20)
    window.addSlider(nbGeneration)

    return window