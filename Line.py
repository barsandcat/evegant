
from Process import Process
from ItemStack import ItemStack
from Schemes import Blueprint, Refine, SchemeToStr

from unittest import TestCase
from unittest.mock import Mock
from logging import warning, error, info

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QPixmap
from scipy.optimize import linprog
from math import ceil

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

	def test_ConstructProgramm(self):
		ORE = 1
		MINERAL = 2
		PART = 3
		SHIP = 4

		refine = Refine(1, "", None, ItemStack(ORE, 1), [ItemStack(MINERAL, 50)])
		blueprint1 = Blueprint(1, "", None, [ItemStack(MINERAL, 10)], ItemStack(PART, 1))
		blueprint2 = Blueprint(2, "", None, [ItemStack(MINERAL, 100), ItemStack(PART, 3)], ItemStack(SHIP, 1) )

		toolkitMock = Mock()
		toolkitMock.GetTypePixmap = Mock(return_value=QPixmap())
		line = Line(blueprint2, toolkitMock)
		line.AddProcess(refine)
		line.AddProcess(blueprint1)
		c, Aub, bub, Aeq, beq  = line.ConstructLinearProgramm()
		self.assertEqual(c, [1, 1, 1])
		self.assertEqual(Aub, [[100, -50, 10], [3, 0, -1]])
		self.assertEqual(bub, [0, 0])
		self.assertEqual(Aeq, [[1, 0, 0]])
		self.assertEqual(beq, [1])

		
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
	def __init__(self, rootProcessScheme, aToolkitTypes, aScene):
		super().__init__()
		self.toolkitTypes = aToolkitTypes
		self.scene = aScene
		self.processes = []
		self.AddProcess(rootProcessScheme)		
		self.processes[0].manual = True


	def Update(self):
		self.beginResetModel()
		
		self.Balance()
		
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
		self.scene.update()

	def AddProcess(self, aScheme):
		process = Process(aScheme)
		process.runsChangedCallback = self.Update
		self.processes.append(process)
		self.Update()

	def ConstructLinearProgramm(self):

		# Caching up:
		tmpMap = {} #ammount[process][item] map: optimization - to avoid searching certain item in process inputs or outputs
		inputs = set() #Unique items used as inputs
		outputs = set() #Unique items used as outputs

		for process in self.processes:
			tmpProcessMap = {}
	
			for inp in process.scheme.GetInputs():
				inputs.add(inp.itemId)
				tmpProcessMap[inp.itemId] = inp.ammount
	
			for out in process.scheme.GetOutputs():
				outputs.add(out.itemId)
				tmpProcessMap[out.itemId] = -out.ammount

			tmpMap[process] = tmpProcessMap
		
		#We optimize (minimizing) sum of all production runs
		c = [1 for proc in self.processes]

		#Iteratin over all itmes that are connected (used) inside line,
		#but not starting items, main product and byproducts
		#Columns are processes, rows - items
		items = inputs.intersection(outputs)
		Aub = []
		bub = []
		for item in items:
			row = []
			for process in self.processes:
				row.append(tmpMap[process].get(item, 0))
			Aub.append(row)
			bub.append(0)

		#Equalities for manual processes
		#Columns are processes, rows - manual processes
		Aeq = []
		beq = []
		for process in self.processes:
			if process.manual:
				row = []
				for process2 in self.processes:
					if process == process2:
						row.append(1)
					else:
						row.append(0)
				
				Aeq.append(row)
				beq.append(process.runs)


		return c, Aub, bub, Aeq, beq
		
	def Balance(self):
		if len(self.processes) < 2:
			return
			
		c, Aub, bub, Aeq, beq = self.ConstructLinearProgramm()
		res = linprog(c, Aub, bub, Aeq, beq)

		if res.success:
			for i in range(len(res.x)):
				self.processes[i].SetRuns(ceil(res.x[i]))
		else:
			error(str(c) + '\n' +  str(Aub)  + '\n' + str(bub)  + '\n' + str(Aeq)  + '\n' + str(beq)  + '\n' + str(res))

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
