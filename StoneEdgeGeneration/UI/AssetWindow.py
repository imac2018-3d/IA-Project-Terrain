import time

from StoneEdgeGeneration.Communication.Communication import Communication
from StoneEdgeGeneration.Asset import genericgenetic
from StoneEdgeGeneration.Asset.generators import crystals
from StoneEdgeGeneration.UI import BaseWindow, Parameter

class AssetWindow(BaseWindow.BaseWindow):
	def __init__(self):
		super(AssetWindow, self).__init__()
		self.setWindowTitle("Asset Generation")

		self.classes = {
			'CrystalGenetic' : ('StoneEdgeGeneration.Asset.generators.crystals', 'CrystalGenetic')
		}

		iterator = iter(self.classes)
		radiobtns = {next(iterator):True}
		try:
			while 1:
				radiobtns[next(iterator)] = False
		except StopIteration:
			pass

		self.genetic_class_UI = Parameter.RadioButtonParameter("Class to generate",radiobtns)
		self.class_buttons = self.addRadioButtons(self.genetic_class_UI)

		self.max_genotypes_UI = Parameter.SliderParameter("Maximum number per generation", 50, 3, 100)
		self.addSlider(self.max_genotypes_UI)

		self.selection_type_UI = Parameter.RadioButtonParameter("Type of selection", {"threshold": True, "number": False, "probability": False})
		self.addRadioButtons(self.selection_type_UI)

		self.selection_type_param_UI = Parameter.RadioButtonParameter("Type of selection parameter", {"threshold": True, "number": False, "probability": False})
		self.addRadioButtons(self.selection_type_UI)

		self.alt_procreation_UI = Parameter.RadioButtonParameter("Alternative procreation", {"True": True, "False": False})
		self.addRadioButtons(self.alt_procreation_UI)

		self.show_mode_UI = Parameter.RadioButtonParameter("Show mode", {"all": True, "solo": False})
		self.addRadioButtons(self.show_mode_UI)

	def startGeneration(self):
		genetic_class = self.classes[self.class_buttons.checkedButton().text()]
		self.max_genotypes = self.max_genotypes_UI.value
		self.selection_type = [key for key, value in self.selection_type_UI.values.items() if value == True][0]
		self.selection_type_param = [key for key, value in self.selection_type_param_UI.values.items() if value == True][0]
		self.alt_procreation = [key for key, value in self.alt_procreation_UI.values.items() if value == True][0]
		self.show_mode = [key for key, value in self.show_mode_UI.values.items() if value == True][0]

		Communication.log(genetic_class)
		Communication.log(self.max_genotypes)
		Communication.log(self.selection_type)
		Communication.log(self.selection_type_param)
		Communication.log(self.alt_procreation)
		Communication.log(self.show_mode)

		try:
			self.assetController = genericgenetic.AssetGeneticsController(genetic_class,
																		  max_genotypes=self.max_genotypes,
																		  selection_type=self.selection_type,
																		  alt_procreation=self.alt_procreation,
																		  show_mode=self.show_mode)
			self.assetController.fill_genotypes()
		except Exception as e:
			Communication.exception(e)
