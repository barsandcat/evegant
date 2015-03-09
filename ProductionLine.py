
from ProductionProcess import ProductionProcess
from unittest import TestCase

from PyQt5.QtCore import QAbstractTableModel, Qt

class ProductionLine(QAbstractTableModel):
	def __init__(self, rootProcessScheme):
		super().__init__()
		self.rootProcess = ProductionProcess(rootProcessScheme)
		self.processes = []
		self.processes.append(self.rootProcess)
		self.Update()

	def Update(self):
		self.inputs = []

		self.items = {}
		for process in self.processes:
			for inp in process.scheme.GetInputs():
				self.items[inp] = self.items.get(inp.itemId, 0) - inp.ammount
			for out in process.scheme.GetOutputs():
				self.items[out] = self.items.get(out.itemId, 0) + out.ammount

		for item, count in self.items.items():
			if count < 0:
				self.inputs.append(item)


	def AddProcess(self, aScheme):
		self.processes.append(ProductionProcess(aScheme))
		self.Update()



	def rowCount(self, parent):
		return len(self.inputs)

	def columnCount(self, parent):
		return 2

	def data(self, index, role):
		if not index.isValid() or role != Qt.DisplayRole:
			return None
		if index.column() == 0:
			return self.inputs[index.row()].itemId
		else:
			return self.inputs[index.row()].ammount		
		return None
