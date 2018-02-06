from importlib import reload
import sys 
from PyQt5 import QtWidgets
from IAProjectTerrain import utils, ui
reload(utils)
reload(ui)

def load():
	try:  
	    app = QtWidgets.QApplication(sys.argv) 
	    window = ui.TerrainWindow()
	    window.show()
	    app.exit(app.exec_())

	except Exception as e:
	    print ('error')
	    print (e)

if __name__ == '__main__':
	load()