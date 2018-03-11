from importlib import reload
import time

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets

from StoneEdgeGeneration.Communication.Communication import Communication
from StoneEdgeGeneration import UI
from StoneEdgeGeneration.UI import Individual, Parameter, FlowLayout
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
			'Terrain': ('StoneEdgeGeneration.Terrain.Map', 'MapGenetic'),
			'Tree' : ('StoneEdgeGeneration.Asset.generators.Tree', 'TreeGenetic')
		}
		self.selectiontypes = {
			"threshold": "threshold", "number": "number", "probability": "probability"
		}
		self.altprocerations = {"True": True, "False": False}

		self.mainLayout = QtWidgets.QVBoxLayout()

		''' TITLE '''
		title = QtWidgets.QLabel("Stone Edge - Assets Generation")
		title.setObjectName("h1")
		self.mainLayout.addWidget(title)

		''' PROGRESS BAR '''
		self.progressBar = QtWidgets.QProgressBar()
		self.progressBar.setRange(0, 100)
		self.progressBar.hide()
		self.mainLayout.addWidget(self.progressBar)

		''' PARAMETERS '''
		self.parametersGBox = QtWidgets.QGroupBox()
		self.parametersVBoxLayout = QtWidgets.QVBoxLayout()
		self.parametersGBox.setLayout(self.parametersVBoxLayout)

		generateButton = QtWidgets.QPushButton()
		generateButton.setObjectName("generate")
		generateButton.setText("Generate")
		generateButton.setToolTip("Generation assets with given parameters")
		generateButton.clicked.connect(self.disableParameters)
		generateButton.clicked.connect(self.startGeneration)

		''' RESULT '''
		resultContent = QtWidgets.QGroupBox()
		self.resultGLayout = FlowLayout.FlowLayout()
		resultContent.setLayout(self.resultGLayout)
		self.maxColumn = 3
		self.elementRow = 0
		self.elementColumn = 0

		self.nextGenerationButton = QtWidgets.QPushButton()
		self.nextGenerationButton.setObjectName("nextGeneration")
		self.nextGenerationButton.setText("Next Generation")
		self.nextGenerationButton.clicked.connect(self.nextGeneration)
		self.nextGenerationButton.setToolTip("Show next generation of assets")

		self.resultGBox = QtWidgets.QScrollArea()
		self.resultGBox.setWidget(resultContent)
		self.resultGBox.setWidgetResizable(True)
		self.resultGBox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.resultGBox.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.resultGBox.setMinimumWidth(400)
		
		self.resultGBox.hide()
		self.nextGenerationButton.hide()

		''' CONTAINER '''
		container = QtWidgets.QGroupBox()
		container.setObjectName("result")
		containerGLayout = QtWidgets.QGridLayout()
		container.setLayout(containerGLayout)
		
		containerGLayout.addWidget(self.parametersGBox, 0, 0)
		containerGLayout.addWidget(generateButton, 1, 0)
		containerGLayout.addWidget(self.resultGBox, 0, 1)
		containerGLayout.addWidget(self.nextGenerationButton, 1, 1)

		self.mainLayout.addWidget(container)

		self.setLayout(self.mainLayout)

		''' INIT PARAMETERS '''
		classParameter = Parameter.RadioButtonParameter("Object to generate", makeRadioParameters(self.classes))
		self.class_btn = self.addRadioButtons(classParameter)
		self.class_btn.buttonPressed.connect(self.clearResults)

		genCountParameter = Parameter.IntParameter("Maximum number per generation", 5, 3, 100, tooltip="Number of assets to generate, per generation")
		self.gen_count_spin = self.addSpinBox(genCountParameter)

		selectionTypeParameter = Parameter.RadioButtonParameter("Type of selection", makeRadioParameters(self.selectiontypes))
		self.select_type_btn = self.addRadioButtons(selectionTypeParameter)
		thresholdParameter = Parameter.FloatParameter("Threshold parameter ", 0.5, 0, 1, 0.05, tooltip="Fitness between 0 and 1")
		self.threshold_parameter = self.addDoubleSpinBox(thresholdParameter)
		numberParameter = Parameter.IntParameter("Number parameter ", 0, 1, self.gen_count_spin.value(), tooltip="Number of best assets to keep")
		self.number_parameter = self.addSpinBox(numberParameter)
		self.gen_count_spin.valueChanged.connect(lambda: self.number_parameter.setMaximum(self.gen_count_spin.value()))

		altProcreationParameter = Parameter.RadioButtonParameter("Alternative procreation", makeRadioParameters(self.altprocerations))
		self.alt_procreation_btn = self.addRadioButtons(altProcreationParameter)

		self.assetController = self.makeAssetController()
		self.individuals = []
		self.individualsWidget = []

	def makeAssetController(self):
		genetic_class = self.classes[self.class_btn.checkedButton().text()]
		max_genotypes = self.gen_count_spin.value()
		selection_type = self.selectiontypes[self.select_type_btn.checkedButton().text()]
		selection_type_param = self.threshold_parameter.value() if selection_type == "threshold" else self.number_parameter.value()
		alt_procreation = self.altprocerations[self.alt_procreation_btn.checkedButton().text()]
		show_mode = 'solo'

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
			selection_type_param = self.threshold_parameter.value() if selection_type == "threshold" else self.number_parameter.value()
			alt_procreation = self.altprocerations[self.alt_procreation_btn.checkedButton().text()]
			show_mode = 'solo'
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

		self.resultGLayout.addWidget(imageGBox)

		# Image
		image = QtWidgets.QPushButton()
		image.setObjectName("image")
		image.pressed.connect(individual.open)
		image.setIconSize(QtCore.QSize(200, 200))
		image.setIcon(QtGui.QIcon(individual.image))
		image.setToolTip("Open asset in Blender")
		imageVLayout.addWidget(image)

		imageGBox.setLayout(imageVLayout)

		# Save button and spinbox
		buttonsGBox = QtWidgets.QGroupBox()
		buttonsVLayout = QtWidgets.QVBoxLayout()
		buttonsGBox.setLayout(buttonsVLayout)

		weightSlider = QtWidgets.QSlider(Qt.Horizontal)
		weightSlider.setMinimum(0)
		weightSlider.setMaximum(100)
		weightSlider.valueChanged.connect(individual.setWeight)
		weightSlider.setValue(individual.weight)
		weightSlider.setToolTip("Weight of the asset for the next generation")
		buttonsVLayout.addWidget(weightSlider)

		saveBtn = QtWidgets.QPushButton()
		saveBtn.setText("Save")
		saveBtn.pressed.connect(individual.createModel)
		saveBtn.setToolTip("Save asset as obj file")
		buttonsVLayout.addWidget(saveBtn)

		imageVLayout.addWidget(buttonsGBox)
		self.individualsWidget.append(imageGBox)

	def generate(self):
		self.resultGBox.show()
		self.nextGenerationButton.show()
		self.progressBar.show()

		self.progressBar.setValue(0)

		if len(self.individuals) > 0:
			for i in range(len(self.individuals)):
				self.assetController.genotypes[self.individuals[i].id].fitness = self.individuals[i].weight
			self.assetController.next_generation()
			self.clearResults()

		self.assetController.fill_genotypes()
		genetic_class = self.classes[self.class_btn.checkedButton().text()]
		for i in range(len(self.assetController.genotypes)):
			genotype = self.assetController.genotypes[i]
			individual = Individual.Individual(i, genotype, type=genetic_class[1])
			data = genotype.process_individual_data()
			Communication.sendcommand(
				"import StoneEdgeGeneration.bpyutils as bpyutils\n"
				"bpyutils.ensure_delete_all()\n"
			)
			Communication.sendcommand(self.assetController.get_genetic_class().net_compute_individual((0, 0, 0), data))
			camerapos = self.assetController.get_genetic_class().camera_position()
			Communication.log(str(camerapos))
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

			self.progressBar.setValue((i+1) * 100 / len(self.assetController.genotypes))

		self.progressBar.hide()
		self.elementColumn = 0
		self.elementRow = 0

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

		spin.setToolTip(parameter.tooltip)

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

		spin.setToolTip(parameter.tooltip)

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

	def disableParameters(self):
		pass
		# self.parametersVBox.setEnabled(True)
		# self.resultGBox.setEnabled(False)