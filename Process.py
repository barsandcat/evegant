
from unittest import TestCase
from unittest.mock import Mock

from Schemes import Blueprint
from ItemStack import ItemStack

class TestProcess(TestCase):

	def test_InitProcess(self):
		scheme = Blueprint(0, "Name", 0, [ItemStack(0, 1)], ItemStack(0, 1))
		process = Process(scheme)
		assert process.inputs[0].ammount == 1

	def test_SetRuns(self):
		scheme = Blueprint(0, "Name", 0, [ItemStack(0, 1)], ItemStack(0, 2))
		process = Process(scheme)
		process.SetRuns(2)
		assert process.inputs[0].ammount == 2
		assert process.outputs[0].ammount == 4

from copy import copy


class Process:

	def __init__(self, aScheme, aRunsChangedCallback):
		self.scheme = aScheme
		self.runs = 1
		self.inputs = [copy(inp) for inp in aScheme.GetInputs()]
		self.outputs = [copy(out) for out in aScheme.GetOutputs()]
		self.runsChangedCallback = aRunsChangedCallback


	def SetRuns(self, aRuns):
		self.runs = aRuns
		schemeInputs = self.scheme.GetInputs()
		for i in range(len(self.inputs)):
			self.inputs[i].ammount = schemeInputs[i].ammount * aRuns

		schemeOutputs = self.scheme.GetOutputs()
		for i in range(len(self.outputs)):
			self.outputs[i].ammount = schemeOutputs[i].ammount * aRuns

		self.runsChangedCallback()



