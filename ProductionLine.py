
from ProductionProcess import ProductionProcess
from unittest import TestCase

class ProductionLine:
	def __init__(self, rootProcessScheme):
		self.rootProcess = ProductionProcess(rootProcessScheme)
		self.processes = []
		self.processes.append(self.rootProcess)
		self.Update()

	def Update(self):
		self.inputs = []
		self.outputs = []

		items = {}
		for process in self.processes:
			for inp in process.scheme.GetInputs():
				items[inp] = items.get(inp, 0) - 1
			for out in process.scheme.GetOutputs():
				items[out] = items.get(out, 0) + 1

		for item, count in items.items():
			if count > 0:
				self.outputs.append(item)
			if count < 0:
				self.inputs.append(item)


	def AddProcess(self, aScheme):
		self.processes.append(ProductionProcess(aScheme))
		self.Update()

