import sys 
import bpy

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets

from StoneEdgeGeneration import utils

class TerrainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TerrainWindow, self).__init__(parent)

        self.mainLayout = QtWidgets.QHBoxLayout()

        self.parametersLayout()
        self.resultLayout()
        
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Terrain Generation")
        
    def resultLayout(self):
        resultGBox = QtWidgets.QGroupBox("Result")
        resultVBoxLayout = QtWidgets.QGridLayout()
        resultGBox.setLayout(resultVBoxLayout)
        self.mainLayout.addWidget(resultGBox)
        
        image1 = self.createImage("coucou", resultVBoxLayout, 0, 0)
        image2 = self.createImage("coucou", resultVBoxLayout, 0, 1)
        image3 = self.createImage("coucou", resultVBoxLayout, 0, 2)
        image4 = self.createImage("coucou", resultVBoxLayout, 2, 0)
        image5 = self.createImage("coucou", resultVBoxLayout, 2, 1)
        image6 = self.createImage("coucou", resultVBoxLayout, 2, 2)
        
        nextGenerationButton = QtWidgets.QPushButton()
        nextGenerationButton.setText("Next Generation")
        resultVBoxLayout.addWidget(nextGenerationButton, 4, 0)
        
        downloadButton = QtWidgets.QPushButton()
        downloadButton.setText("Download Selection")
        resultVBoxLayout.addWidget(downloadButton, 4, 2)
        
    def parametersLayout(self):
        parametersGBox = QtWidgets.QGroupBox("Parameters")
        parametersVBoxLayout = QtWidgets.QVBoxLayout()
        parametersGBox.setLayout(parametersVBoxLayout)
        self.mainLayout.addWidget(parametersGBox)
        
        param1 = self.createParameter("Parameter 1", parametersVBoxLayout)
        param2 = self.createParameter("Parameter 2", parametersVBoxLayout)
        param3 = self.createParameter("Parameter 3", parametersVBoxLayout)
        param4 = self.createParameter("Parameter 4", parametersVBoxLayout)
        
        generateButton = QtWidgets.QPushButton()
        generateButton.setText("Generate")
        parametersVBoxLayout.addWidget(generateButton)
        
    def createParameter(self, title, layout, min=0, max=100):
        sliderLabel = QtWidgets.QLabel()
        sliderLabel.setText(title)
        layout.addWidget(sliderLabel)
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setMinimum(min)
        slider.setMaximum(max)
        layout.addWidget(slider)
        
        return slider
    
    def createImage(self, imageName, gridLayout, row, column):
        image = QtWidgets.QPushButton()
        pixmap = QtGui.QPixmap(utils.getImagePath(imageName))
        ButtonIcon = QtGui.QIcon(pixmap)
        image.setIcon(ButtonIcon)
        image.setIconSize(QtCore.QSize(100, 100))
        gridLayout.addWidget(image, row, column)
        
        spinBox = QtWidgets.QSpinBox()
        gridLayout.addWidget(spinBox, row+1, column)
        
        return image
