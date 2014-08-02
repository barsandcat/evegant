#!/usr/bin/python3


import math
import sqlite3

from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
		QSizeF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
		QPainterPath, QPen, QPixmap, QPolygonF)
from PyQt5.QtWidgets import (QAction, QApplication, QButtonGroup, QComboBox,
		QFontComboBox, QGraphicsItem, QGraphicsLineItem, QGraphicsPolygonItem,
		QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
		QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QSizePolicy,
		QToolBox, QToolButton, QWidget, QTreeView, QSplitter, QSplashScreen)

from logging import warning, error, info

from ProductionLineScene import ProcessGraphic, ConstructProcessGraphicTree, FillScene
from ProductionScheme import ProductionScheme
from ProductionLine import ProductionLine
from Schemes import CreateSchemesTree
from ToolkitTypes import ToolkitTypes
from EveTypesModel import EveTypesModel
from SchemesFilterModel import SchemesFilterModel
from ToolkitBlueprints import LoadBlueprints


class MainWindow(QMainWindow):
 
	def __init__(self, connection, blueprints, toolkitTypes):
		super().__init__()

		self.toolkitTypes = toolkitTypes
		self.productionLine = None

		
		#Tree view setup
		treeRoot = CreateSchemesTree(connection, blueprints)
		model = EveTypesModel(treeRoot)
		self.filterModel = SchemesFilterModel()
		self.filterModel.setSourceModel(model)
		
		self.treeView = QTreeView()
		self.treeView.doubleClicked.connect(self.OnTreeDoubleClick)
		self.treeView.setModel(self.filterModel)


		self.scene = QGraphicsScene()
		self.view = QGraphicsView(self.scene)
		self.view.setMinimumWidth(500)

		splitter = QSplitter()
		splitter.addWidget(self.treeView)
		splitter.addWidget(self.view)

		self.setCentralWidget(splitter)
		self.setWindowTitle("EveGant")

		self.createMenus()
		self.createToolbars()

	def	SetupGraphView(self):
		graphics = [ProcessGraphic(process, self.toolkitTypes) for process in self.productionLine.processes]
		ConstructProcessGraphicTree(graphics)

		FillScene(self.scene, graphics)			
		

	def OnTreeDoubleClick(self, aIndex):
		data = self.treeView.model().data(aIndex, Qt.UserRole)

		if data.GetChildCount() == 0:
			if self.productionLine:
				self.productionLine.AddProcess(data)
			else:
				self.productionLine = ProductionLine(data)
			self.filterModel.outputs = self.productionLine.inputs
			self.filterModel.invalidateFilter()
			self.SetupGraphView()

	def sceneScaleChanged(self, scale):
		newScale = float(scale[:-1]) / 100.0
		oldMatrix = self.view.transform()
		self.view.resetTransform()
		self.view.translate(oldMatrix.dx(), oldMatrix.dy())
		self.view.scale(newScale, newScale)

	def about(self):
		QMessageBox.about(self, "EveGant", "Eve online industrial planning and traking tool")

	def createMenus(self):
		exitAction = QAction("E&xit", self, shortcut="Ctrl+X",
				statusTip="Quit Scenediagram example", triggered=self.close)

		aboutAction = QAction("A&bout", self, shortcut="Ctrl+B",
				triggered=self.about)

		fileMenu = self.menuBar().addMenu("&File")
		fileMenu.addAction(exitAction)

		aboutMenu = self.menuBar().addMenu("&Help")
		aboutMenu.addAction(aboutAction)

	def createToolbars(self):

		sceneScaleCombo = QComboBox()
		sceneScaleCombo.addItems(["50%", "75%", "100%", "125%", "150%"])
		sceneScaleCombo.setCurrentIndex(2)
		sceneScaleCombo.currentIndexChanged[str].connect(self.sceneScaleChanged)

		pointerToolbar = self.addToolBar("Pointer type")
		pointerToolbar.addWidget(sceneScaleCombo)


if __name__ == '__main__':

	import sys
	
	app = QApplication(sys.argv)
	
	splash = QSplashScreen(QPixmap("Splash.jpg"))
	splash.show()
	app.processEvents()
	
	
	splash.showMessage("Loading icons")
	app.processEvents()
	toolkitTypes = ToolkitTypes()
	
	splash.showMessage("Loading data base")
	app.processEvents()
	dbFileName = "Eve toolkit/DATADUMP201407101530.db"
	connection = sqlite3.connect(dbFileName)
	
	splash.showMessage("Loading blueprints")
	app.processEvents()
	blueprints = LoadBlueprints()

	mainWindow = MainWindow(connection, blueprints, toolkitTypes)
	mainWindow.setGeometry(100, 100, 800, 500)
	mainWindow.show()
	splash.finish(mainWindow)

	sys.exit(app.exec_())
