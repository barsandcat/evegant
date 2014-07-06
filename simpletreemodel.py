#!/usr/bin/python3


from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QTreeView

import simpletreemodel_rc

import sqlite3

from logging import warning, info, error

from EveDB import BluePrint, LoadBlueprint, Refine, LoadRefine

class MarketGroup:
	def __init__(self, aName, aParent=None):
		self.parent = aParent
		self.name = aName
		self.children = []

	def AppendChild(self, aItem):
		self.children.append(aItem)

	def SetParent(self, aParent):
		self.parent = aParent

	def GetChild(self, row):
		return self.children[row]

	def GetChildCount(self):
		return len(self.children)

	def GetIndexOfChild(self, aChild):
		return self.children.index(aChild)

	def GetName(self):
		return self.name

	def GetParent(self):
		return self.parent


class LazyMarketGroup:
	def __init__(self, aMarketGroupId, aName, aParent, aDBConnection):
		self.parent = aParent
		self.name = aName
		self.children = None
		self.marketGroupId = aMarketGroupId
		self.db = aDBConnection

	def CacheChildren(self):
		if self.children == None:
			self.children = []
			cursor = self.db.cursor()
			#Load child market groups
			cursor.execute("SELECT marketGroupID, marketGroupName "
				"FROM invMarketGroups WHERE parentGroupID = ?", 
				(self.marketGroupId,))			
			
			for row in cursor:
				marketGroupId = row[0]
				name = row[1]
				self.children.append(LazyMarketGroup(marketGroupId, name, self, self.db))

			#Load child types, if it is blueprint - should have not null blueprintID
			cursor.execute("SELECT typeID, blueprintTypeID "
				"FROM invTypes LEFT JOIN invBlueprintTypes ON typeID = blueprintTypeID "
				"WHERE marketGroupID = ?", (self.marketGroupId,))

			for row in cursor:
				if row[1]:
					blueprint = LoadBlueprint(self.db.cursor(), row[1], self)
					self.children.append(blueprint)
				else:
					refine = LoadRefine(self.db.cursor(), row[0], self)
					self.children.append(refine)


	def GetChild(self, row):
		self.CacheChildren()
		return self.children[row]

	def GetChildCount(self):
		self.CacheChildren()
		return len(self.children)

	def GetIndexOfChild(self, aChild):
		self.CacheChildren()
		return self.children.index(aChild)

	def GetName(self):
		return self.name

	def GetParent(self):
		return self.parent



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


def SetupModelData():
	rootItem = MarketGroup("Type")
	connection = sqlite3.connect("Eve toolkit/DATADUMP201403101147.db")

	rootItem.AppendChild(LazyMarketGroup(2, "Blueprints", rootItem, connection))
	rootItem.AppendChild(LazyMarketGroup(54, "Ore", rootItem, connection))
	rootItem.AppendChild(LazyMarketGroup(493, "Ice Ore", rootItem, connection))
	return rootItem



if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)

	rootItem = SetupModelData()

	model = EveTypesModel(rootItem)

	view = QTreeView()
	view.setModel(model)
	view.setWindowTitle("Simple Tree Model")
	view.show()
	sys.exit(app.exec_())
