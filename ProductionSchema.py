

class ProductionSchema:
	def __init__(self, aSchemaId, aInputs, aOutputs):
		assert aSchemaId > 0
		assert aOutputs
		assert len(aOutputs) > 0
		self.schemaId = aSchemaId
		self.inputs = aInputs
		self.outputs = aOutputs
		
	def GetName(self):
		return str(self.schemaId)