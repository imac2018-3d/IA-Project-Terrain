from importlib import reload
import sys 
from PyQt5 import QtWidgets, QtCore
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

# # register class stuff 
# class PyQtEventTerrain(): 
#     _timer = None 
#     _window = None 

#     def execute(self): 
#         self._application = QtWidgets.QApplication.instance() 
#         self._application = QtWidgets.QApplication(['']) 
#         self._eventLoop = QtCore.QEventLoop() 

#         self.window = TerrainWindow.TerrainWindow()
#         # EXAMPLE OF SLIDER PARAMETER
#         nbGeneration = Parameter.SliderParameter("Number of generations", 15, 10, 20)
#         self.window.addSlider(nbGeneration)
#         print(nbGeneration.value)
#         self.window.show() 

# class ExampleQtWindow(QtWidgets.QDialog): 
#     def __init__(self): 
#         super(ExampleQtWindow, self).__init__() 
#         self.mainLayout = QtWidgets.QVBoxLayout(self) 
#         self.buttonLayout = QtWidgets.QHBoxLayout() 
#         self.CreateButton = QtWidgets.QPushButton("print info") 
#         self.CreateButton.clicked.connect(self.testCommand) 
#         self.mainLayout.addWidget(self.CreateButton) 
#         self.setLayout(self.mainLayout) 

#     def testCommand(self): 
#         print(bpy.data.objects) 

# def loadTerrain():
    

# def loadAsset():
#   try:  
#       app = QtWidgets.QApplication(sys.argv) 
#       window = AssetWindow.AssetWindow()

#       ''' EXAMPLE OF SLIDER PARAMETER '''
#       # Create a new slider between 10 and 20, with value equal to 15 and label "Number of generations"
#       nbGeneration = Parameter.SliderParameter("Number of generations", value=15, min=10, max=20)
#       window.addSlider(nbGeneration)

#       window.show()
#       app.exit(app.exec_())

#       print("running in background") 
#           new_window = PyQtEvent() 
#           new_window.execute()

#   except Exception as e:
#       print ('error')
#       print (e)

# if __name__ == '__main__':
#   loadTerrain()
#   loadAsset()


def loadAsset():
    window = AssetWindow.AssetWindow()

    # EXAMPLE OF SLIDER PARAMETER
    nbGeneration = Parameter.SliderParameter("Number of generations", 15, 10, 20)
    window.addSlider(nbGeneration)

    return window

def loadTerrain():
    window = TerrainWindow.TerrainWindow()
    
    # EXAMPLE OF SLIDER PARAMETER
    nbGeneration = Parameter.SliderParameter("Number of generations", 15, 10, 20)
    window.addSlider(nbGeneration)

    return window