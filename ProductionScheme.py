

class ProductionScheme:
	def __init__(self, aSchemeId, aInputs, aOutputs):
		assert aSchemeId > 0
		assert aOutputs
		assert len(aOutputs) > 0
		self.schemeId = aSchemeId
		self.inputs = aInputs
		self.outputs = aOutputs
		