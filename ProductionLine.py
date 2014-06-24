
from ProductionScheme import ProductionScheme
from ProductionProcess import ProductionProcess


import unittest
import unittest.mock

class TestProductionLine(unittest.TestCase):

	def test_AddProcess(self):
		assert False


class ProductionLine:
	def __init__(self, rootProcessScheme):
		self.rootProcess = ProductionProcess(rootProcessScheme)

	def AddProcess():
		pass

	def GetAviableSchemes():
		return []
