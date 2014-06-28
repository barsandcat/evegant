
from ProductionScheme import ProductionScheme
from ProductionLine import ProductionLine

from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
		QSizeF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
		QPainterPath, QPen, QPixmap, QPolygonF)
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsLineItem, QGraphicsScene)


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

def GetCenteredRectF(width, height):
	x = width / 2 - width
	y = height / 2 - height
	return QRectF(x, y, width, height)	

class ProcessGraphic(QGraphicsItem):
	def __init__(self, aProductionProcess):
		super().__init__()
		self.process = aProductionProcess
		self.children = []
		self.parents = []
		self.col = 0
		self.row = 0
		self.rect = GetCenteredRectF(200, 200)

	def AddChild(self, aGraphic):
		if aGraphic not in self.children:
			self.children.append(aGraphic)

	def AddParent(self, aGraphic):
		if aGraphic not in self.parents:
			self.parents.append(aGraphic)

	def paint(self, painter, option, widget=None):
		painter.fillRect(self.rect, Qt.white)
		painter.drawRoundedRect(self.rect, 10, 10)
		painter.drawText(QPointF(0, 0), self.process.scheme.GetName())

	def boundingRect(self):
		return self.rect



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
	sceneWidth = colWidth * maxCol
	sceneHeight = rowHeigth * maxRow
	aScene.setSceneRect(QRectF(0, 0, sceneHeight, sceneWidth))
	aScene.clear()

	## Set process positions
	for graphic in aGraphics:
		x = sceneWidth - (graphic.col + 0.5) * colWidth
		y = (graphic.row + 0.5) * rowHeigth
		graphic.setPos(QPointF(x, y))
		aScene.addItem(graphic)

	## Add lines
	queue = [aGraphics[0]]
	done = set()
	while queue:
		graphic = queue.pop(0)
		if graphic not in done:
			done.add(graphic)
			queue.extend(graphic.children)
			for parent in graphic.parents:
				line = QGraphicsLineItem(QLineF(parent.pos(), graphic.pos()))
				line.setZValue(-1000)
				aScene.addItem(line)
