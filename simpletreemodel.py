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

class TreeItem:
	def __init__(self, aName, parent=None):
		self.parentItem = parent
		self.name = aName
		self.childItems = []

	def AppendChild(self, item):
		self.childItems.append(item)

	def Child(self, row):
		return self.childItems[row]

	def ChildCount(self):
		return len(self.childItems)

	def GetName(self):
		return self.name

	def Parent(self):
		return self.parentItem

	def Row(self):
		if self.parentItem:
			return self.parentItem.childItems.index(self)

		return 0


class EveTypesModel(QAbstractItemModel):
	def __init__(self, aRootItem):
		super().__init__(None)
		self.rootItem = aRootItem

	def columnCount(self, parent):
		return 1

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
		if not self.hasIndex(row, column, parent):
			return QModelIndex()

		if not parent.isValid():
			parentItem = self.rootItem
		else:
			parentItem = parent.internalPointer()

		childItem = parentItem.Child(row)
		if childItem:
			return self.createIndex(row, column, childItem)
		else:
			return QModelIndex()

	def parent(self, index):
		if not index.isValid():
			return QModelIndex()

		childItem = index.internalPointer()
		parentItem = childItem.Parent()

		if parentItem == self.rootItem:
			return QModelIndex()

		return self.createIndex(parentItem.Row(), 0, parentItem)

	def rowCount(self, parent):
		if parent.column() > 0:
			return 0

		if not parent.isValid():
			parentItem = self.rootItem
		else:
			parentItem = parent.internalPointer()

		return parentItem.ChildCount()


def SetupModelData():
	rootItem = TreeItem("Type")
	connection = sqlite3.connect("Eve toolkit/DATADUMP201403101147.db")
	cursor = connection.cursor()
	cursor.execute("SELECT marketGroupID, parentGroupID, marketGroupName, iconID FROM invMarketGroups")
	marketGroups = {}
	for row in cursor:            
		groupID = row[0]
		parentID = row[1]
		groupName = row[2]
		marketGroups[groupID] = TreeItem(groupName, parentID)
	
	for key, child in marketGroups.items():
		parentID = child.Parent()
		if parentID:
			parent = marketGroups[parentID]
		else:
			parent = rootItem
		child.parentItem = parent
		parent.AppendChild(child)

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
