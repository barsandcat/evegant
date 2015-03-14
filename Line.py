
from Process import Process
from unittest import TestCase
from logging import warning, error, info

from PyQt5.QtCore import QAbstractTableModel, Qt

class Line(QAbstractTableModel):
	def __init__(self, rootProcessScheme):
		super().__init__()
		self.processes = []
		self.AddProcess(rootProcessScheme)
		self.rootProcess = self.processes[0]


	def Update(self):
		self.inputs = []

		self.items = {}
		for process in self.processes:
			for inp in process.inputs:
				self.items[inp] = self.items.get(inp.itemId, 0) - inp.ammount
			for out in process.outputs:
				self.items[out] = self.items.get(out.itemId, 0) + out.ammount

		for item, count in self.items.items():
			if count < 0:
				self.inputs.append(item)

		self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(None), 1))


	def AddProcess(self, aScheme):
		self.processes.append(Process(aScheme, self.Update))
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
