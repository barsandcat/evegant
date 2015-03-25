
from Process import Process
from ItemStack import ItemStack
from Schemes import Blueprint, Refine, SchemeToStr

from unittest import TestCase
from unittest.mock import Mock
from logging import warning, error, info

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QPixmap

class TestLine(TestCase):

	def test_SimpleLine(self):
		item1 = ItemStack(1, 1)
		item2 = ItemStack(2, 1)
		item3 = ItemStack(3, 1)
		bluePrint1 = Blueprint(1, "", None, [item2], item1)
		refine1 = Refine(1, "", None, item3, [item2])

		toolkitMock = Mock()
		toolkitMock.GetTypePixmap = Mock(return_value=QPixmap())
		line = Line(bluePrint1, toolkitMock)
		line.AddProcess(refine1)
		self.assertEqual(len(line.balance), 2)
		self.assertEqual(line.balance[0].itemId, 1)
		self.assertEqual(line.balance[0].ammount, 1)
		self.assertEqual(line.balance[1].itemId, 3)
		self.assertEqual(line.balance[1].ammount, -1)
		
	def test_BalanceOreRefine(self):
		bantamBlueprint = Blueprint(1, "", None,
			[		
			ItemStack(34, 22222),
			ItemStack(35, 8000 ),
			ItemStack(36, 2444 ),
			ItemStack(37, 500  ),
			ItemStack(38, 2    ),
			ItemStack(39, 2    ),
			],
			ItemStack(582, 1))
				
		omber = Refine(2, "", None,
			ItemStack(1227, 100),
			[
			ItemStack(34, 85),
			ItemStack(35, 34),
			ItemStack(37, 85),
			])
		
		plagioclase = Refine(3, "", None,
			ItemStack(18, 100),
			[
			ItemStack(34, 107),
			ItemStack(35, 213),
			ItemStack(36, 107),
			])
		
		scordite = Refine(4, "", None,
			ItemStack(1228, 100),
			[
			ItemStack(34, 346),
			ItemStack(35, 173),
			])

		toolkitMock = Mock()
		toolkitMock.GetTypePixmap = Mock(return_value=QPixmap())
		line = Line(bantamBlueprint, toolkitMock)
		line.AddProcess(omber)
		line.AddProcess(plagioclase)
		line.AddProcess(scordite)
		line.Balance()
		self.assertGreater(line.processes[1].runs, 1)
		self.assertGreater(line.processes[2].runs, 1)
		self.assertGreater(line.processes[3].runs, 1)


class Line(QAbstractTableModel):
	def __init__(self, rootProcessScheme, aToolkitTypes):
		super().__init__()
		self.toolkitTypes = aToolkitTypes
		self.processes = []
		self.AddProcess(rootProcessScheme)
		self.rootProcess = self.processes[0]


	def Update(self):
		self.beginResetModel()
		
		self.inputs = []
		self.balance = []

		items = {}
		for process in self.processes:
			for inp in process.inputs:
				items[inp.itemId] = items.get(inp.itemId, 0) - inp.ammount
			for out in process.outputs:
				items[out.itemId] = items.get(out.itemId, 0) + out.ammount

		for itemId, count in items.items():
			if count != 0:
				self.balance.append(ItemStack(itemId, count))
			if count < 0:
				self.inputs.append(itemId)
		


		self.endResetModel()

	def AddProcess(self, aScheme):
		process = Process(aScheme)
		warning(SchemeToStr(aScheme))
		process.runsChangedCallback = self.Update
		self.processes.append(process)
		self.Update()
		
	def Balance(self):
		pass


	def rowCount(self, parent):
		return len(self.balance)

	def columnCount(self, parent):
		return 2

	def data(self, index, role):
		if not index.isValid():
			return None

		if index.column() == 0:
			if role == Qt.DecorationRole:
				return self.toolkitTypes.GetTypePixmap(self.balance[index.row()].itemId, 32)
		else:
			if role == Qt.DisplayRole:
				return self.balance[index.row()].ammount

		return None
