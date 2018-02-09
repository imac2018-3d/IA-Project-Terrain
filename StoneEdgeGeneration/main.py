from importlib import reload
import sys 
from PyQt5 import QtWidgets
from StoneEdgeGeneration import utils, UI, Terrain, Asset
reload(utils)
reload(UI)
reload(Terrain)
reload(Asset)
from StoneEdgeGeneration.UI import TerrainWindow, AssetWindow, Parameter, Individual
reload(TerrainWindow)
reload(AssetWindow)
reload(Parameter)
reload(Individual)

def loadTerrain():
	try:  
	    app = QtWidgets.QApplication(sys.argv) 
	    window = TerrainWindow.TerrainWindow()

	    # EXAMPLE OF SLIDER PARAMETER
	    nbGeneration = Parameter.SliderParameter("Number of generations", 15, 10, 20)
	    window.addSlider(nbGeneration)
	    print(nbGeneration.value)

	    window.show()
	    app.exit(app.exec_())

	except Exception as e:
	    print ('error')
	    print (e)

def loadAsset():
	try:  
	    app = QtWidgets.QApplication(sys.argv) 
	    window = AssetWindow.AssetWindow()

	    ''' EXAMPLE OF SLIDER PARAMETER '''
	    # Create a new slider between 10 and 20, with value equal to 15 and label "Number of generations"
	    nbGeneration = Parameter.SliderParameter("Number of generations", value=15, min=10, max=20)
	    window.addSlider(nbGeneration)

	    ''' EXAMPLE OF CREATION OF 5 INDIVIDUALS OF TYPE "CRYSTAL" '''
	    for i in range(5):
	    	# Create an individual of type "Crystal"
	    	individual = Individual.Individual(i, type="Crystal")
	    	# Create an image of this individual
	    	individual.createImage()
	    	window.addIndividual(individual)

	    window.show()
	    app.exit(app.exec_())

	except Exception as e:
	    print ('error')
	    print (e)

if __name__ == '__main__':
	loadTerrain()
	loadAsset()