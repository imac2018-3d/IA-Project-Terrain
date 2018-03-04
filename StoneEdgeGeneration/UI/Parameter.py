class Parameter:
	def __init__(self, label):
		self.label = label


class IntParameter(Parameter):
	def __init__(self, label, value, min, max):
		super(IntParameter, self).__init__(label)
		self.value = value
		self.min = min
		self.max = max

	def setValue(self, value):
		self.value = value
		print(self.value)

class FloatParameter(Parameter):
	def __init__(self, label, value, min, max, step):
		super(FloatParameter, self).__init__(label)
		self.value = value
		self.min = min
		self.max = max
		self.step = step

	def setValue(self, value):
		self.value = value
		print(self.value)


class RadioButtonParameter(Parameter):
	def __init__(self, label, values):
		super(RadioButtonParameter, self).__init__(label)
		self.values = values

	def checked(self):
		for key, value in self.values.items():
			if value:
				return key
		else:
			return self.values[0]
