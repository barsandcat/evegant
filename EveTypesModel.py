
from PyQt5.QtCore import Qt, QAbstractItemModel,  QModelIndex


class EveTypesModel(QAbstractItemModel):
	def __init__(self, aRootItem):
		super().__init__(None)
		self.rootItem = aRootItem

	def columnCount(self, parent):
		#For simple tree, column is always 0
		return 1

	def rowCount(self, parent):
		#For tree rowCount is children count
		if parent.column() > 0:
			return 0

		if not parent.isValid():
			parentItem = self.rootItem
		else:
			parentItem = parent.internalPointer()

		return parentItem.GetChildCount()

	def data(self, index, role):
		if not index.isValid():
			return None

		if role == Qt.UserRole:
			return index.internalPointer()

		if role != Qt.DisplayRole:
			return None

		item = index.internalPointer()

		return item.GetName()

	def flags(self, index):
		if not index.isValid():
			return Qt.NoItemFlags

		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self.rootItem.GetName()

		return None

	def index(self, row, column, parent):
		#Return QModelIndex with item, by child index(row) of a parent. Column is irrelevant
		if not self.hasIndex(row, column, parent):
			return QModelIndex()

		if not parent.isValid():
			parentItem = self.rootItem
		else:
			parentItem = parent.internalPointer()

		childItem = parentItem.GetChild(row)
		if childItem:
			return self.createIndex(row, column, childItem)
		else:
			return QModelIndex()

	def parent(self, index):
		#Retrieving the parent QModelIndex from a child is a bit more work than
		#finding a parent's child. We can easily retrieve the parent node using
		#internalPointer() and going up using the Node's parent pointer, but to
		#obtain the row number (the position of the parent among its siblings),
		#we need to go back to the grandparent and find the parent's index
		#position in its parent's (i.e., the child's grandparent's) list of
		#children.
		if not index.isValid():
			return QModelIndex()

		item = index.internalPointer()
		parent = item.GetParent()
		if not parent:
			return QModelIndex()

		if parent == self.rootItem:
			return QModelIndex()

		row = 0
		grandParent = parent.GetParent()
		if grandParent:
			row = grandParent.GetIndexOfChild(parent)

		return self.createIndex(row, 0, parent)
