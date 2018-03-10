class Parameter:
	def __init__(self, label):
		self.label = label


class IntParameter(Parameter):
	def __init__(self, label, value, min, max, tooltip=None):
		super(IntParameter, self).__init__(label)
		self.value = value
		self.min = min
		self.max = max
		self.tooltip = tooltip

	def setValue(self, value):
		self.value = value
		print(self.value)

class FloatParameter(Parameter):
	def __init__(self, label, value, min, max, step, tooltip=None):
		super(FloatParameter, self).__init__(label)
		self.value = value
		self.min = min
		self.max = max
		self.step = step
		self.tooltip = tooltip

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
