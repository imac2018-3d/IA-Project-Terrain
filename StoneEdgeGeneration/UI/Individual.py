from importlib import reload
from StoneEdgeGeneration import utils
reload(utils)

class Individual:
	def __init__(self, id, weight=50, type="Asset"):
		self.id = id
		self.weight = weight
		self.type = type

	def createImage(self):
		self.image = self.type + str(self.id)
		utils.saveImage(self.image)

	def setWeight(self, weight):
		self.weight = weight