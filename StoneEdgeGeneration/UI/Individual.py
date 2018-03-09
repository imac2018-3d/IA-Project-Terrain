class Individual:
	def __init__(self, id, weight=50, type="Asset"):
		self.id = id
		self.weight = weight
		self.type = type

	def createImage(self):
		from StoneEdgeGeneration import bpyutils
		self.image = str(self)
		bpyutils.saveImage(self.image)

	def createModel(self):
		Communication.log("CREATE MODEL - Individual")
		print("HEEEEY")
		from StoneEdgeGeneration import bpyutils
		# self.model = "coucou"
		Communication.sendcommand(
			"import StoneEdgeGeneration.bpyutils as bpyutils\n"
			"bpyutils.saveModel('coucou'))\n"
			"client.send(0)\n"
		)

	def setImage(self, imagename):
		self.image = imagename

	def setModel(self, modelname):
		self.model = modelname


	def setWeight(self, weight):
		self.weight = weight

	def __str__(self):
		return self.type + str(self.id)
