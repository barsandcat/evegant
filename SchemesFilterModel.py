
from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex, Qt

from unittest import TestCase
from unittest.mock import Mock

from EveTypesModel import EveTypesModel
from Schemes import Blueprint
from MarketGroup import MarketGroup

class TestSchemesFilterModel(TestCase):

	def test_filterEmpty(self):
		flt = SchemesFilterModel()
		self.assertTrue(flt.filterAcceptsRow(0, QModelIndex()))

	def test_filterPass(self):
		flt = SchemesFilterModel()
		root = MarketGroup("Root")
		root.AppendChild(Blueprint(1, "Name", None, [], 1))
		source = EveTypesModel(root)
		flt.outputs = [0, 1, 2]
		flt.setSourceModel(source)
		self.assertTrue(flt.filterAcceptsRow(0, QModelIndex()))

	def test_filterGroup(self):
		root = MarketGroup("Root")
		group = MarketGroup("Group")
		root.AppendChild(group)
		group.AppendChild(Blueprint(1, "Name", None, [], 1))
		source = EveTypesModel(root)

		flt = SchemesFilterModel()
		flt.outputs = [0, 1, 2]
		flt.setSourceModel(source)
		self.assertTrue(flt.filterAcceptsRow(0, QModelIndex()))


class SchemesFilterModel(QSortFilterProxyModel):
	def __init__(self):
		super().__init__()
		self.outputs = set()

	def filterAcceptsRow(self, sourceRow, sourceParent):
		if not self.outputs:
			return True

		index = self.sourceModel().index(sourceRow, 0, sourceParent)
		data = self.sourceModel().data(index, Qt.UserRole)

		if data.GetChildCount() > 0:
			rowCount = self.sourceModel().rowCount(index)
			for i in range(rowCount):
				if self.filterAcceptsRow(i, index):
					return True
		else:
			for out in data.GetOutputs():
				if out in self.outputs:
					return True

		return False

		

		

