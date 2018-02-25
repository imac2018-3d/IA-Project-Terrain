from importlib import reload
import bpy

from StoneEdgeGeneration import utils, UI, Asset
from StoneEdgeGeneration.Asset import genericgenetic
from StoneEdgeGeneration.Asset.generators import crystals
reload(crystals)
from StoneEdgeGeneration.UI import BaseWindow, Parameter
reload(utils)
reload(UI)
reload(BaseWindow)
reload(Parameter)

class AssetWindow(BaseWindow.BaseWindow):
    def __init__(self):
        super(AssetWindow, self).__init__()
        self.setWindowTitle("Asset Generation")

        self.genetic_class_UI = Parameter.RadioButtonParameter("Class to generate", {"CrystalGenetic": True})
        self.addRadioButtons(self.genetic_class_UI)

        self.max_genotypes_UI = Parameter.SliderParameter("Maximum number per generation", 50, 10, 100)
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
        self.genetic_class = [key for key, value in self.genetic_class_UI.values.items() if value == True][0]
        self.max_genotypes = self.max_genotypes_UI.value
        self.selection_type = [key for key, value in self.selection_type_UI.values.items() if value == True][0]
        self.selection_type_param = [key for key, value in self.selection_type_param_UI.values.items() if value == True][0]
        self.alt_procreation = [key for key, value in self.alt_procreation_UI.values.items() if value == True][0]
        self.show_mode = [key for key, value in self.show_mode_UI.values.items() if value == True][0]

        print(self.genetic_class)
        print(self.max_genotypes)
        print(self.selection_type)
        print(self.selection_type_param)
        print(self.alt_procreation)
        print(self.show_mode)

        print(bpy.context)

        self.assetController = genericgenetic.AssetGeneticsController(crystals.CrystalGenetic, max_genotypes=self.max_genotypes, selection_type=self.selection_type, alt_procreation=self.alt_procreation, show_mode=self.show_mode)
        # for i in range(5):
        #     individual = Individual.Individual(i, type="Crystal")
        #     individual.createImage()
        #     self.addIndividual(individual)
