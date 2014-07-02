
from ProductionSchema import ProductionSchema
from ProductionProcess import ProductionProcess


import unittest
import unittest.mock

class TestProductionLine(unittest.TestCase):

	def test_AddProcess(self):
		line = ProductionLine(ProductionSchema(1, [2], [1]))
		assert line.outputs[0] == 1
		assert len(line.outputs) == 1
		assert line.inputs[0] == 2
		assert len(line.inputs) == 1
		line.AddProcess(ProductionSchema(2, [3], [2]))
		assert line.outputs[0] == 1
		assert len(line.outputs) == 1
		assert line.inputs[0] == 3
		assert len(line.inputs) == 1


class ProductionLine:
	def __init__(self, rootProcessSchema):
		self.rootProcess = ProductionProcess(rootProcessSchema)
		self.processes = []
		self.processes.append(self.rootProcess)
		self.Update()

	def Update(self):
		self.inputs = []
		self.outputs = []

		items = {}
		for process in self.processes:
			for inp in process.schema.GetInputs():
				items[inp] = items.get(inp, 0) - 1
			for out in process.schema.GetOutputs():
				items[out] = items.get(out, 0) + 1

		for item, count in items.items():
			if count > 0:
				self.outputs.append(item)
			if count < 0:
				self.inputs.append(item)


	def AddProcess(self, aSchema):
		self.processes.append(ProductionProcess(aSchema))
		self.Update()

	def GetAviableSchemas():
		return []
