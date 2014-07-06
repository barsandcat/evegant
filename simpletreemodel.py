#!/usr/bin/python3


from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QTreeView

import sqlite3

from logging import warning, info, error

from EveTypesModel import EveTypesModel

from MarketGroup import MarketGroup, LazyMarketGroup

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
