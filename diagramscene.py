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

from ProductionScheme import ProductionScheme
from ProductionLine import ProductionLine

import math

from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
		QSizeF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
		QPainterPath, QPen, QPixmap, QPolygonF)
from PyQt5.QtWidgets import (QAction, QApplication, QButtonGroup, QComboBox,
		QFontComboBox, QGraphicsItem, QGraphicsLineItem, QGraphicsPolygonItem,
		QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
		QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QSizePolicy,
		QToolBox, QToolButton, QWidget)

import diagramscene_rc



import unittest
import unittest.mock

class TestProductionLineScene(unittest.TestCase):

	def test_ConstructTree(self):
		line = ProductionLine(ProductionScheme(1, [2, 3], [4]))
		line.AddProcess(ProductionScheme(2, [1], [2]))
		line.AddProcess(ProductionScheme(2, [1], [3]))
		graphics = ConstructProcessGraphicTree(line)
		root = graphics[0]
		assert root.process == line.processes[0]
		assert not root.parents
		assert len(root.children) == 2
		assert not root.children[0].children
		assert not root.children[1].children

	def test_ConstructCyclesTree(self):
		line = ProductionLine(ProductionScheme(1, [3, 4], [5]))
		line.AddProcess(ProductionScheme(2, [2], [3]))
		line.AddProcess(ProductionScheme(3, [1], [2, 4]))
		graphics = ConstructProcessGraphicTree(line)
		root = graphics[0]
		assert not root.parents
		assert len(root.children) == 2
		assert len(root.children[0].parents) == 2 or len(root.children[1].parents) == 2

	def test_ConstructMultipleOutputsTree(self):
		line = ProductionLine(ProductionScheme(1, [3, 4], [5]))
		line.AddProcess(ProductionScheme(2, [2], [3]))
		line.AddProcess(ProductionScheme(3, [1], [3, 4]))
		graphics = ConstructProcessGraphicTree(line)
		root = graphics[0]
		assert not root.parents
		assert len(root.children) == 2
		assert len(root.children[0].parents) == 1
		assert len(root.children[1].parents) == 1


class ProcessGraphic(QGraphicsItem):
	def __init__(self, aProductionProcess):
		super().__init__()
		self.process = aProductionProcess
		self.children = []
		self.parents = []
		self.col = 0
		self.row = 0

	def AddChild(self, aGraphic):
		if aGraphic not in self.children:
			self.children.append(aGraphic)

	def AddParent(self, aGraphic):
		if aGraphic not in self.parents:
			self.parents.append(aGraphic)

	def paint(self, painter, option, widget=None):
		painter.drawRoundedRect(-100, -100, 200, 200, 10, 10)

	def boundingRect(self):
		return QRectF(-100, -100, 200, 200)


def ConstructProcessGraphicTree(aProductionLine):
	graphics = [ProcessGraphic(process) for process in aProductionLine.processes]

	outputsOwners = {}
	for graphic in graphics:
		for out in graphic.process.scheme.outputs:
			outputsOwners.setdefault(out, []).append(graphic)
	
	for parent in graphics:
		for inp in parent.process.scheme.inputs:
			if inp in outputsOwners:
				children = outputsOwners[inp]
				for child in children:
					parent.AddChild(child)
					child.AddParent(parent)

	assert not graphics[0].parents
	return graphics

def FillScene(aScene, aGraphics):	
	## Findout process column
	maxCol = 0
	queue = [aGraphics[0]]
	done = set()
	while queue:
		graphic = queue.pop(0)
		if graphic not in done:
			done.add(graphic)
			for child in graphic.children:
				child.col = max(child.col, graphic.col + 1)
				maxCol = max(maxCol, child.col)
				queue.append(child)
	maxCol = maxCol + 1

	## Findout process row
	maxRow = 0
	processRows = [0 for i in range(maxCol + 1)]
	for graphic in aGraphics:
		graphic.row = processRows[graphic.col]
		processRows[graphic.col] = processRows[graphic.col] + 1
		maxRow = max(maxRow, graphic.row)
	maxRow = maxRow + 1

	colWidth = 250
	rowHeigth = 250
	aScene.setSceneRect(QRectF(0, 0, colWidth * maxCol, rowHeigth * maxRow))
	aScene.clear()

	for graphic in aGraphics:
		x = (graphic.col + 0.5) * colWidth
		y = (graphic.row + 0.5) * rowHeigth
		graphic.setPos(QPointF(x, y))
		aScene.addItem(graphic)


class Arrow(QGraphicsLineItem):
	def __init__(self, startItem, endItem, parent=None, scene=None):
		super(Arrow, self).__init__(parent)

		self.arrowHead = QPolygonF()

		self.myStartItem = startItem
		self.myEndItem = endItem
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)
		self.myColor = Qt.black
		self.setPen(QPen(self.myColor, 2, Qt.SolidLine, Qt.RoundCap,
				Qt.RoundJoin))

	def setColor(self, color):
		self.myColor = color

	def startItem(self):
		return self.myStartItem

	def endItem(self):
		return self.myEndItem

	def boundingRect(self):
		extra = (self.pen().width() + 20) / 2.0
		p1 = self.line().p1()
		p2 = self.line().p2()
		return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

	def shape(self):
		path = super(Arrow, self).shape()
		path.addPolygon(self.arrowHead)
		return path

	def updatePosition(self):
		line = QLineF(self.mapFromItem(self.myStartItem, 0, 0), self.mapFromItem(self.myEndItem, 0, 0))
		self.setLine(line)

	def paint(self, painter, option, widget=None):
		if (self.myStartItem.collidesWithItem(self.myEndItem)):
			return

		myStartItem = self.myStartItem
		myEndItem = self.myEndItem
		myColor = self.myColor
		myPen = self.pen()
		myPen.setColor(self.myColor)
		arrowSize = 20.0
		painter.setPen(myPen)
		painter.setBrush(self.myColor)

		centerLine = QLineF(myStartItem.pos(), myEndItem.pos())
		endPolygon = myEndItem.polygon()
		p1 = endPolygon.first() + myEndItem.pos()

		intersectPoint = QPointF()
		for i in endPolygon:
			p2 = i + myEndItem.pos()
			polyLine = QLineF(p1, p2)
			intersectType = polyLine.intersect(centerLine, intersectPoint)
			if intersectType == QLineF.BoundedIntersection:
				break
			p1 = p2

		self.setLine(QLineF(intersectPoint, myStartItem.pos()))
		line = self.line()

		angle = math.acos(line.dx() / line.length())
		if line.dy() >= 0:
			angle = (math.pi * 2.0) - angle

		arrowP1 = line.p1() + QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
										math.cos(angle + math.pi / 3) * arrowSize)
		arrowP2 = line.p1() + QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
										math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

		self.arrowHead.clear()
		for point in [line.p1(), arrowP1, arrowP2]:
			self.arrowHead.append(point)

		painter.drawLine(line)
		painter.drawPolygon(self.arrowHead)
		if self.isSelected():
			painter.setPen(QPen(myColor, 1, Qt.DashLine))
			myLine = QLineF(line)
			myLine.translate(0, 4.0)
			painter.drawLine(myLine)
			myLine.translate(0,-8.0)
			painter.drawLine(myLine)
	

class MainWindow(QMainWindow):
 
	def __init__(self):
		super(MainWindow, self).__init__()

		self.productionLine = ProductionLine(ProductionScheme(1, [2, 3], [4]))
		self.productionLine.AddProcess(ProductionScheme(2, [1], [2]))
		self.productionLine.AddProcess(ProductionScheme(2, [1], [3]))

		self.scene = QGraphicsScene()

		graphics = ConstructProcessGraphicTree(self.productionLine)
		FillScene(self.scene, graphics)
			
		self.createActions()
		self.createMenus()
		self.createToolBox()


		self.createToolbars()

		layout = QHBoxLayout()
		layout.addWidget(self.toolBox)
		self.view = QGraphicsView(self.scene)
		layout.addWidget(self.view)

		self.widget = QWidget()
		self.widget.setLayout(layout)

		self.setCentralWidget(self.widget)
		self.setWindowTitle("Diagramscene")

	def buttonGroupClicked(self, id):
		buttons = self.buttonGroup.buttons()
		for button in buttons:
			if self.buttonGroup.button(id) != button:
				button.setChecked(False)

	def sceneScaleChanged(self, scale):
		newScale = scale.left(scale.indexOf("%")).toDouble()[0] / 100.0
		oldMatrix = self.view.matrix()
		self.view.resetMatrix()
		self.view.translate(oldMatrix.dx(), oldMatrix.dy())
		self.view.scale(newScale, newScale)

	def about(self):
		QMessageBox.about(self, "About Diagram Scene",
				"The <b>Diagram Scene</b> example shows use of the graphics framework.")

	def createToolBox(self):
		self.buttonGroup = QButtonGroup()
		self.buttonGroup.setExclusive(False)
		self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

		button = QToolButton()
		button.setIconSize(QSize(50, 50))
		button.setCheckable(False)
		self.buttonGroup.addButton(button)

		layout = QGridLayout()
		layout.addWidget(button, 0, 1)

		itemWidget = QWidget()
		itemWidget.setLayout(layout)

		self.toolBox = QToolBox()
		self.toolBox.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored))
		self.toolBox.setMinimumWidth(itemWidget.sizeHint().width())
		self.toolBox.addItem(itemWidget, "Basic Flowchart Shapes")

	def createActions(self):
		self.exitAction = QAction("E&xit", self, shortcut="Ctrl+X",
				statusTip="Quit Scenediagram example", triggered=self.close)

		self.aboutAction = QAction("A&bout", self, shortcut="Ctrl+B",
				triggered=self.about)

	def createMenus(self):
		self.fileMenu = self.menuBar().addMenu("&File")
		self.fileMenu.addAction(self.exitAction)

		self.aboutMenu = self.menuBar().addMenu("&Help")
		self.aboutMenu.addAction(self.aboutAction)

	def createToolbars(self):

		self.sceneScaleCombo = QComboBox()
		self.sceneScaleCombo.addItems(["50%", "75%", "100%", "125%", "150%"])
		self.sceneScaleCombo.setCurrentIndex(2)
		self.sceneScaleCombo.currentIndexChanged[str].connect(self.sceneScaleChanged)

		self.pointerToolbar = self.addToolBar("Pointer type")
		self.pointerToolbar.addWidget(self.sceneScaleCombo)


if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)

	mainWindow = MainWindow()
	mainWindow.setGeometry(100, 100, 800, 500)
	mainWindow.show()

	sys.exit(app.exec_())
