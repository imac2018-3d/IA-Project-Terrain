class Parameter:
	def __init__(self, label, value):
		self.label = label
		self.value = value

	def setValue(self, value):
		self.value = value
		print(self.value)

class SliderParameter(Parameter):
	def __init__(self, label, value, min, max):
		super(SliderParameter, self).__init__(label, value)
		self.min = min
		self.max = max