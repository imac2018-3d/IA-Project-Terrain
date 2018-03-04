from importlib import reload
import time

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets

from StoneEdgeGeneration.Communication.Communication import Communication
from StoneEdgeGeneration import UI
from StoneEdgeGeneration.UI import Individual, Parameter
from StoneEdgeGeneration.Asset import genericgenetic
reload(UI)

def makeRadioParameters(options):
	iterator = iter(options)
	radioparameter = {next(iterator): True}
	try:
		while 1:
			radioparameter[next(iterator)] = False
	except StopIteration:
		pass
	return radioparameter

class BaseWindow(QtWidgets.QWidget):
	def __init__(self):
		super(BaseWindow, self).__init__()
		self.classes = {
			'Crystal': ('StoneEdgeGeneration.Asset.generators.crystals', 'CrystalGenetic'),
			'Terrain': ('StoneEdgeGeneration.Terrain.Map', 'MapGenetic')
		}
		self.selectiontypes = {
			"threshold": "threshold", "number": "number", "probability": "probability"
		}
		self.altprocerations = {"True": True, "False": False}
		self.showmodes = {
			'all': 'all', 'solo': 'solo'
		}

		self.mainLayout = QtWidgets.QGridLayout()

		''' PARAMETERS '''
		self.parametersGBox = QtWidgets.QGroupBox("Parameters")
		self.parametersVBoxLayout = QtWidgets.QVBoxLayout()
		self.parametersGBox.setLayout(self.parametersVBoxLayout)
		self.mainLayout.addWidget(self.parametersGBox, 0, 0)

		generateButton = QtWidgets.QPushButton()
		generateButton.setText("Generate")
		generateButton.clicked.connect(self.startGeneration)
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
		nextGenerationButton.clicked.connect(self.nextGeneration)
		self.mainLayout.addWidget(nextGenerationButton, 1, 1)

		self.setLayout(self.mainLayout)

		classParameter = Parameter.RadioButtonParameter("Object to generate", makeRadioParameters(self.classes))
		self.class_btn = self.addRadioButtons(classParameter)
		self.class_btn.buttonPressed.connect(self.clearResults)

		genCountParameter = Parameter.IntParameter("Maximum number per generation", 5, 3, 100)
		self.gen_count_spin = self.addSpinBox(genCountParameter)

		selectionTypeParameter = Parameter.RadioButtonParameter("Type of selection", makeRadioParameters(self.selectiontypes))
		self.select_type_btn = self.addRadioButtons(selectionTypeParameter)
		selectionTypeParamParameter = Parameter.FloatParameter("Selection param", 0.5, 0, 1, 0.05)
		self.select_type_param_spin = self.addDoubleSpinBox(selectionTypeParamParameter)

		altProcreationParameter = Parameter.RadioButtonParameter("Alternative procreation", makeRadioParameters(self.altprocerations))
		self.alt_procreation_btn = self.addRadioButtons(altProcreationParameter)

		showModeParameter = Parameter.RadioButtonParameter("Show mode", makeRadioParameters(self.showmodes))
		self.show_mode_btn = self.addRadioButtons(showModeParameter)

		self.assetController = self.makeAssetController()
		self.individuals = []
		self.individualsWidget = []

	def makeAssetController(self):
		genetic_class = self.classes[self.class_btn.checkedButton().text()]
		max_genotypes = self.gen_count_spin.value()
		selection_type = self.selectiontypes[self.select_type_btn.checkedButton().text()]
		selection_type_param = self.select_type_param_spin.value()
		alt_procreation = self.altprocerations[self.alt_procreation_btn.checkedButton().text()]
		show_mode = self.showmodes[self.show_mode_btn.checkedButton().text()]

		Communication.log(genetic_class)
		Communication.log(max_genotypes)
		Communication.log(selection_type)
		Communication.log(selection_type_param)
		Communication.log(alt_procreation)
		Communication.log(show_mode)

		return genericgenetic.AssetGeneticsController(genetic_class,
													  max_genotypes=max_genotypes,
													  selection_type=selection_type,
													  selection_type_param=selection_type_param,
													  alt_procreation=alt_procreation,
													  show_mode=show_mode)

	def updateAssetController(self):
		if self.assetController is None:
			self.assetController = self.makeAssetController()
		else:
			genetic_class = self.classes[self.class_btn.checkedButton().text()]
			max_genotypes = self.gen_count_spin.value()
			selection_type = self.selectiontypes[self.select_type_btn.checkedButton().text()]
			selection_type_param = self.select_type_param_spin.value()
			alt_procreation = self.altprocerations[self.alt_procreation_btn.checkedButton().text()]
			show_mode = self.showmodes[self.show_mode_btn.checkedButton().text()]
			self.assetController.reset(genetic_class,
									  max_genotypes=max_genotypes,
									  selection_type=selection_type,
									  selection_type_param=selection_type_param,
									  alt_procreation=alt_procreation,
									  show_mode=show_mode)


	def startGeneration(self):
		try:
			self.clearResults()
			self.updateAssetController()
			self.generate()
		except Exception as e:
			Communication.exception(e)

	def nextGeneration(self):
		try:
			self.updateAssetController()
			self.generate()
		except Exception as e:
			Communication.exception(e)


	def addIndividual(self, individual):
		self.individuals.append(individual)
		imageGBox = QtWidgets.QGroupBox()
		imageVLayout = QtWidgets.QVBoxLayout()

		self.resultGLayout.addWidget(imageGBox, self.elementRow, self.elementColumn)
		if self.elementColumn < self.maxColumn:
			self.elementColumn += 1
		else:
			self.elementColumn = 0
			self.elementRow += 1

		# Image
		image = QtWidgets.QPushButton()
		image.setIconSize(QtCore.QSize(100, 100))
		image.setIcon(QtGui.QIcon(individual.image))
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
		self.individualsWidget.append(imageGBox)

	def generate(self):
		if len(self.individuals) > 0:
			for i in range(len(self.individuals)):
				self.assetController.genotypes[self.individuals[i].id].fitness = self.individuals[i].weight
			self.assetController.next_generation()
			self.clearResults()

		self.assetController.fill_genotypes()
		genetic_class = self.classes[self.class_btn.checkedButton().text()]
		for i in range(len(self.assetController.genotypes)):
			genotype = self.assetController.genotypes[i]
			individual = Individual.Individual(i, type=genetic_class[1])
			data = genotype.process_individual_data()
			Communication.sendcommand(
				"import StoneEdgeGeneration.bpyutils as bpyutils\n"
				"bpyutils.ensure_delete_all()\n"
			)
			Communication.sendcommand(self.assetController.get_genetic_class().net_compute_individual((0, 0, 0), data))
			camerapos = self.assetController.get_genetic_class().camera_position()
			Communication.sendcommand(
				"import StoneEdgeGeneration.utils as utils\n"
				"print(utils.getImagePath('" + str(individual) + "'))\n"
				"client.send(utils.getImagePath('" + str(individual) + "'))\n"
			)
			imgpath = Communication.receivedata(None)
			Communication.sendcommand(
				"import StoneEdgeGeneration.bpyutils as bpyutils\n"
				"bpyutils.saveImage('" + imgpath + "', "
					"("+str(camerapos[0])+", "+str(camerapos[1])+", "+str(camerapos[2])+"))\n"
				"client.send(0)\n"
			)
			Communication.receivedata(None)
			individual.setImage(imgpath)
			self.addIndividual(individual)

	def addButton(self, action):
		btn = QtWidgets.QPushButton()
		btn.setText(action.label)
		self.parametersVBoxLayout.addWidget(btn)

		btn.pressed.connect(action.trigger)
		return btn

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
		return slider

	def addSpinBox(self, parameter):
		lbl = QtWidgets.QLabel()
		lbl.setText(parameter.label)
		self.parametersVBoxLayout.addWidget(lbl)
		spin = QtWidgets.QSpinBox()

		spin.setValue(parameter.value)
		spin.setMinimum(parameter.min)
		spin.setMaximum(parameter.max)

		spin.valueChanged.connect(parameter.setValue)

		self.parametersVBoxLayout.addWidget(spin)
		return spin

	def addDoubleSpinBox(self, parameter):
		lbl = QtWidgets.QLabel()
		lbl.setText(parameter.label)
		self.parametersVBoxLayout.addWidget(lbl)
		spin = QtWidgets.QDoubleSpinBox()

		spin.setValue(parameter.value)
		spin.setMinimum(parameter.min)
		spin.setMaximum(parameter.max)
		spin.setSingleStep(parameter.step)

		spin.valueChanged.connect(parameter.setValue)

		self.parametersVBoxLayout.addWidget(spin)
		return spin

	def addRadioButtons(self, parameter):
		buttonLabel = QtWidgets.QLabel()
		buttonLabel.setText(parameter.label)
		self.parametersVBoxLayout.addWidget(buttonLabel)

		grpBtn = QtWidgets.QButtonGroup(self.parametersGBox)

		for key, value in parameter.values.items():
			btn = QtWidgets.QRadioButton(key)
			btn.setChecked(value)
			grpBtn.addButton(btn)
			self.parametersVBoxLayout.addWidget(btn)

		return grpBtn

	def clearResults(self):
		print("Clear")
		while len(self.individualsWidget) > 0:
			widget = self.individualsWidget.pop()
			widget.deleteLater()
		self.individuals.clear()

