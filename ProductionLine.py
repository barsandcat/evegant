
from ProductionScheme import ProductionScheme
from ProductionProcess import ProductionProcess


import unittest
import unittest.mock

class TestProductionLine(unittest.TestCase):

	def test_AddProcess(self):
		line = ProductionLine(ProductionScheme(1, [2], [1]))
		assert len(line.inputs) == 1
		assert line.outpus[0] == 1
		assert line.inputs[0] == 2
		line.AddProcess(ProductionScheme(2, [3], [2]))
		assert line.outpus[0] == 1
		assert line.inputs[0] == 3


class ProductionLine:
	def __init__(self, rootProcessScheme):
		self.rootProcess = ProductionProcess(rootProcessScheme)

	def AddProcess(self, scheme):
		pass

	def GetAviableSchemes():
		return []
