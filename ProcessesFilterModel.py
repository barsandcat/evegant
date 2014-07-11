
from PyQt5.QtCore import QSortFilterProxyModel, Qt

class ProcessesFilterModel(QSortFilterProxyModel):
	def __init__(self):
		super().__init__()
		self.outputs = set()

	def filterAcceptsRow(self, sourceRow, sourceParent):
		if not self.outputs:
			return True

		index = self.sourceModel().index(sourceRow, 0, sourceParent)
		
		rowOutputs = self.sourceModel().data(index, Qt.UserRole).GetOutputs()
		for out in rowOutputs:
			if out in self.outputs:
				return True

		return False

		

