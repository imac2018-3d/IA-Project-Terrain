class Individual:
	def __init__(self, id, weight=50, type="Asset"):
		self.id = id
		self.weight = weight
		self.type = type

	def createImage(self):
		from StoneEdgeGeneration import bpyutils
		self.image = str(self)
		bpyutils.saveImage(self.image)

	def setImage(self, imagename):
		self.image = imagename

	def setWeight(self, weight):
		self.weight = weight

	def __str__(self):
		return self.type + str(self.id)
