from StoneEdgeGeneration.Communication.Communication import Communication

class Individual:
	def __init__(self, id, genotype, weight=50, type="Asset"):
		self.id = id
		self.weight = weight
		self.type = type
		self.genotype = genotype

	def createImage(self):
		Communication.sendcommand(
			"import StoneEdgeGeneration.bpyutils as bpyutils\n"
			"print ('yolo ma gueule')"
			"bpyutils.saveImage('"+self.image+"')\n"
		)

	def createModel(self):
		self.model = str(self)
		self.open()
		Communication.sendcommand(
			"import StoneEdgeGeneration.bpyutils as bpyutils\n"
			"bpyutils.saveModel('" + self.model + "')\n"
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

	def open(self):
		Communication.log("Open individual")


		data = self.genotype.process_individual_data()
		Communication.sendcommand(
			"import StoneEdgeGeneration.bpyutils as bpyutils\n"
			"bpyutils.ensure_delete_all()\n"
		)
		Communication.sendcommand(self.genotype.__class__.net_compute_individual((0, 0, 0), data))