from importlib import reload
import sys 
from PyQt5 import QtWidgets
from StoneEdgeGeneration import utils, ui, Terrain, Asset
reload(utils)
reload(ui)

def loadTerrain():
	try:  
	    app = QtWidgets.QApplication(sys.argv) 
	    window = ui.TerrainWindow()
	    window.show()
	    app.exit(app.exec_())

	except Exception as e:
	    print ('error')
	    print (e)

def loadAsset():
	try:  
	    app = QtWidgets.QApplication(sys.argv) 
	    window = ui.AssetWindow()
	    window.show()
	    app.exit(app.exec_())

	except Exception as e:
	    print ('error')
	    print (e)

if __name__ == '__main__':
	loadTerrain()
	loadAsset()