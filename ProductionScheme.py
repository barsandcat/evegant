

class ProductionScheme:
	def __init__(self, id, input, output):
		assert id > 0
		assert output
		self.id = id
		self.input = input
		self.output = output
		