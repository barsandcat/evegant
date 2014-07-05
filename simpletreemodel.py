#!/usr/bin/python3


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QTreeView

import simpletreemodel_rc

import sqlite3

from logging import warning, info, error

connection = None
def GetDBCursor():
	global connection
	if not connection:
		connection = sqlite3.connect("Eve toolkit/DATADUMP201403101147.db")
	return connection.cursor()

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
	def __init__(self, aMarketGroupId, aName, aParent=None):
		self.parent = aParent
		self.name = aName
		self.children = None
		self.marketGroupId = aMarketGroupId

	def CacheChildren(self):
		if self.children == None:
			cursor = GetDBCursor()
			cursor.execute("SELECT marketGroupID, marketGroupName FROM invMarketGroups WHERE parentGroupID = ?", 
				(self.marketGroupId,))
			
			self.children = []
			for row in cursor:
				marketGroupId = row[0]
				name = row[1]
				self.children.append(LazyMarketGroup(marketGroupId, name, self))


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
	rootItem.AppendChild(LazyMarketGroup(2, "Blueprints", rootItem))
	rootItem.AppendChild(LazyMarketGroup(54, "Ore", rootItem))
	rootItem.AppendChild(LazyMarketGroup(493, "Ice Ore", rootItem))
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
