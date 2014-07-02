
from ProductionSchema import ProductionSchema
from ProductionLine import ProductionLine

from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
		QSizeF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
		QPainterPath, QPen, QPixmap, QPolygonF)
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsScene)


import unittest
import unittest.mock
import zipfile

typesArchive = None

class TestProductionLineScene(unittest.TestCase):

	def test_ConstructTree(self):
		line = ProductionLine(ProductionSchema(1, [2, 3], [4]))
		line.AddProcess(ProductionSchema(2, [1], [2]))
		line.AddProcess(ProductionSchema(2, [1], [3]))
		graphics = ConstructProcessGraphicTree(line)
		assert len(graphics[0].inputs[0].children) == 1
		assert len(graphics[0].inputs[1].children) == 1
		assert len(graphics[1].inputs[0].children) == 0
		assert len(graphics[2].inputs[0].children) == 0

	def test_ConstructCyclesTree(self):
		line = ProductionLine(ProductionSchema(1, [3, 4], [5]))
		line.AddProcess(ProductionSchema(2, [2], [3]))
		line.AddProcess(ProductionSchema(3, [1], [2, 4]))
		graphics = ConstructProcessGraphicTree(line)

		assert len(graphics[0].inputs[0].children) == 1
		assert len(graphics[0].inputs[1].children) == 1
		assert len(graphics[1].inputs[0].children) == 1
		assert len(graphics[2].inputs[0].children) == 0

	def test_ConstructMultipleOutputsTree(self):
		line = ProductionLine(ProductionSchema(1, [3, 4], [5]))
		line.AddProcess(ProductionSchema(2, [2], [3]))
		line.AddProcess(ProductionSchema(3, [1], [3, 4]))
		graphics = ConstructProcessGraphicTree(line)

		assert len(graphics[0].inputs[0].children) == 2
		assert len(graphics[0].inputs[1].children) == 1
		assert len(graphics[1].inputs[0].children) == 0
		assert len(graphics[2].inputs[0].children) == 0


class ItemStackGraphic(QGraphicsItem):
	def __init__(self, aItemId, aParent, aPos):
		super().__init__(aParent)
		self.setPos(aPos)
		self.itemId = aItemId
		self.rect = QRectF(-35, 0, 70, 35)
		self.children = []
		icon = QGraphicsPixmapItem(GetTypePixmap(aItemId, 32), self)
		icon.setPos(QPointF(-33, 2))

	def paint(self, painter, option, widget=None):
		painter.fillRect(self.rect, Qt.white)
		painter.drawRect(self.rect)

	def GetInScenePos(self):
		return self.scenePos() + QPointF(-35, 17)

	def GetOutScenePos(self):
		return self.scenePos() + QPointF(35, 17)

	def boundingRect(self):
		return self.rect

def GetTypePixmap(aTypeId, aSize):
	pixmap = QPixmap()

	global typesArchive
	if not typesArchive:
		typesArchive = zipfile.ZipFile('Eve toolkit/Rubicon_1.3_Types.zip')

	filename = 'Types/{0}_{1}.png'.format(aTypeId, aSize)
	pixmap.loadFromData(typesArchive.read(filename))

	return pixmap


class ProcessGraphic(QGraphicsItem):
	def __init__(self, aProductionProcess):
		super().__init__()
		self.process = aProductionProcess
		self.col = 0
		self.row = 0
		self.inputs = []
		self.outputs = []

		icon = QGraphicsPixmapItem(GetTypePixmap(self.process.schema.schemaId, 32), self)
		
		width = 200
		inputOffset = 0
		space = 40

		for inp in self.process.schema.GetInputs():
			inputOffset = inputOffset + space
			itemStack = ItemStackGraphic(inp, self, QPointF(0, inputOffset))
			self.inputs.append(itemStack)

		outputOffset = 0
		for out in self.process.schema.GetOutputs():
			outputOffset = outputOffset + space
			itemStack = ItemStackGraphic(out, self, QPointF(width, outputOffset))
			self.outputs.append(itemStack)

		self.rect = QRectF(0, 0, width, max(outputOffset, inputOffset) + space)


	def GetChildren(self):
		children = set()
		for inp in self.inputs:
			for childOut in inp.children:
				childProcess = childOut.parentItem()
				children.add(childProcess)

		return children

	def paint(self, painter, option, widget=None):
		painter.fillRect(self.rect, Qt.white)
		painter.drawRoundedRect(self.rect, 10, 10)
		painter.drawText(self.rect, Qt.AlignHCenter + Qt.AlignVCenter, self.process.schema.GetName())

	def boundingRect(self):
		return self.rect




def ConstructProcessGraphicTree(aProductionLine):
	graphics = [ProcessGraphic(process) for process in aProductionLine.processes]

	outputsByItemId = {}
	for graphic in graphics:
		for out in graphic.outputs:
			outputsByItemId.setdefault(out.itemId, []).append(out)
	
	for parentProcess in graphics:
		for inp in parentProcess.inputs:
			if inp.itemId in outputsByItemId:
				outputs = outputsByItemId[inp.itemId]
				for out in outputs:
					inp.children.append(out)

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
			children = graphic.GetChildren()
			for child in children:
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

	colWidth = 300
	rowHeigth = 200
	sceneWidth = colWidth * maxCol
	sceneHeight = rowHeigth * maxRow
	aScene.setSceneRect(QRectF(0, 0, sceneHeight, sceneWidth))
	aScene.clear()

	## Set process positions
	for graphic in aGraphics:
		x = sceneWidth - (graphic.col + 1) * colWidth
		y = 50 + graphic.row * rowHeigth
		graphic.setPos(QPointF(x, y))
		aScene.addItem(graphic)

	## Add lines
	for graphic in aGraphics:
		for inp in graphic.inputs:
			for child in inp.children:
				line = QGraphicsLineItem(QLineF(child.GetOutScenePos(), inp.GetInScenePos()))
				line.setZValue(-1000)
				aScene.addItem(line)

