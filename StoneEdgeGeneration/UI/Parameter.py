class Parameter:
	def __init__(self, label):
		self.label = label

class SliderParameter(Parameter):
	def __init__(self, label, value, min, max):
		super(SliderParameter, self).__init__(label)
		self.value = value
		self.min = min
		self.max = max

	def setValue(self, value):
		self.value = value
		print(self.value)

class RadioButtonParameter(Parameter):
	def __init__(self, label, values):
		super(RadioButtonParameter, self).__init__(label)
		self.values = values

	def checked(self):
		for key, value in values.items():
			if(value == True):
				return key
				break
		else:
			return values[0]