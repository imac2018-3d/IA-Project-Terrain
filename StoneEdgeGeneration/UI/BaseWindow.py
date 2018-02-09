import sys 
import bpy
from importlib import reload

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets

from StoneEdgeGeneration import UI, utils
reload(utils)
from StoneEdgeGeneration.UI import Parameter
reload(UI)
reload(Parameter)

class BaseWindow(QtWidgets.QWidget):
    def __init__(self):
        super(BaseWindow, self).__init__()

        self.mainLayout = QtWidgets.QGridLayout()

        ''' PARAMETERS '''
        self.parametersGBox = QtWidgets.QGroupBox("Parameters")
        self.parametersVBoxLayout = QtWidgets.QVBoxLayout()
        self.parametersGBox.setLayout(self.parametersVBoxLayout)
        self.mainLayout.addWidget(self.parametersGBox, 0, 0)
              
        generateButton = QtWidgets.QPushButton()
        generateButton.setText("Generate")
        self.mainLayout.addWidget(generateButton, 1, 0)

        ''' RESULT '''
        self.resultGBox = QtWidgets.QGroupBox("Result")
        self.resultGLayout = QtWidgets.QGridLayout()
        self.resultGBox.setLayout(self.resultGLayout)
        self.mainLayout.addWidget(self.resultGBox, 0, 1)
        self.maxColumn = 4
        self.elementRow = 0
        self.elementColumn = 0
        
        nextGenerationButton = QtWidgets.QPushButton()
        nextGenerationButton.setText("Next Generation")
        self.mainLayout.addWidget(nextGenerationButton, 1, 1)

        self.setLayout(self.mainLayout)
                 
    def addIndividual(self, individual):
        imageGBox = QtWidgets.QGroupBox()
        imageVLayout = QtWidgets.QVBoxLayout()

        self.resultGLayout.addWidget(imageGBox, self.elementRow, self.elementColumn)
        if(self.elementColumn < self.maxColumn):
            self.elementColumn += 1
        else:
            self.elementColumn = 0
            self.elementRow += 1

        # Image
        image = QtWidgets.QPushButton()
        pixmap = QtGui.QPixmap(utils.getImagePath(individual.image))
        ButtonIcon = QtGui.QIcon(pixmap)
        image.setIcon(ButtonIcon)
        image.setIconSize(QtCore.QSize(100, 100))
        imageVLayout.addWidget(image)

        imageGBox.setLayout(imageVLayout)

        # Save button and spinbox
        buttonsGBox = QtWidgets.QGroupBox()
        buttonsHLayout = QtWidgets.QHBoxLayout()
        buttonsGBox.setLayout(buttonsHLayout)

        weightSBox = QtWidgets.QSpinBox()
        weightSBox.valueChanged.connect(individual.setWeight)
        weightSBox.setValue(individual.weight)
        buttonsHLayout.addWidget(weightSBox)

        saveBtn = QtWidgets.QPushButton()
        saveBtn.setText("Save")
        buttonsHLayout.addWidget(saveBtn)

        imageVLayout.addWidget(buttonsGBox)

    def addSlider(self, parameter):
        sliderLabel = QtWidgets.QLabel()
        sliderLabel.setText(parameter.label)
        self.parametersVBoxLayout.addWidget(sliderLabel)
        slider = QtWidgets.QSlider(Qt.Horizontal)
        
        slider.setValue(parameter.value)
        slider.setMinimum(parameter.min)
        slider.setMaximum(parameter.max)

        slider.valueChanged.connect(parameter.setValue)

        self.parametersVBoxLayout.addWidget(slider)