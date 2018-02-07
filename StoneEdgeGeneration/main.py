from importlib import reload
import sys 
from PyQt5 import QtWidgets
from StoneEdgeGeneration import utils, UI, Terrain, Asset
from StoneEdgeGeneration.UI import TerrainWindow, AssetWindow
reload(utils)
reload(UI)
reload(Terrain)
reload(Asset)
reload(TerrainWindow)
reload(AssetWindow)

def loadTerrain():
	try:  
	    app = QtWidgets.QApplication(sys.argv) 
	    window = TerrainWindow.TerrainWindow()
	    window.show()
	    app.exit(app.exec_())

	except Exception as e:
	    print ('error')
	    print (e)

def loadAsset():
	try:  
	    app = QtWidgets.QApplication(sys.argv) 
	    window = AssetWindow.AssetWindow()
	    window.show()
	    app.exit(app.exec_())

	except Exception as e:
	    print ('error')
	    print (e)

if __name__ == '__main__':
	loadTerrain()
	#loadAsset()