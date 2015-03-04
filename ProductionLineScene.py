
from ProductionLine import ProductionLine
from ProductionProcess import ProductionProcess
from Schemes import Blueprint, Refine
from ItemStack import ItemStack

from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
		QSizeF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
		QPainterPath, QPen, QPixmap, QPolygonF)
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsPixmapItem, QGraphicsPathItem, QGraphicsScene, QGraphicsProxyWidget, QSpinBox


from unittest import TestCase
from unittest.mock import Mock


def DummyBlueprint(inputs, output):
	return Blueprint(0, "", None, [ItemStack(inpId, 1) for inpId in inputs], ItemStack(output, 2));

def DummyRefine(input, outputs):
	return Refine(0, "", None,  ItemStack(input, 3), [ItemStack(outId, 4) for outId in outputs]);


class TestProductionLineScene(TestCase):

	def test_ConstructTree(self):
		tookitMock = Mock()
		tookitMock.GetTypePixmap = Mock(return_value=QPixmap())

		graphics = []
		graphics.append(ProcessGraphic(ProductionProcess(DummyBlueprint([2, 3], 4)), tookitMock))
		graphics.append(ProcessGraphic(ProductionProcess(DummyBlueprint([1], 2)), tookitMock))
		graphics.append(ProcessGraphic(ProductionProcess(DummyBlueprint([1], 3)), tookitMock))

		ConstructProcessGraphicTree(graphics)

		assert len(graphics[0].inputs[0].children) == 1
		assert len(graphics[0].inputs[1].children) == 1
		assert len(graphics[1].inputs[0].children) == 0
		assert len(graphics[2].inputs[0].children) == 0

	def test_ConstructCyclesTree(self):
		tookitMock = Mock()
		tookitMock.GetTypePixmap = Mock(return_value=QPixmap())

		graphics = []
		graphics.append(ProcessGraphic(ProductionProcess(DummyBlueprint([3, 4], 5)), tookitMock))
		graphics.append(ProcessGraphic(ProductionProcess(DummyBlueprint([2], 3)), tookitMock))
		graphics.append(ProcessGraphic(ProductionProcess(DummyRefine(1, [2, 4])), tookitMock))

		ConstructProcessGraphicTree(graphics)

		assert len(graphics[0].inputs[0].children) == 1
		assert len(graphics[0].inputs[1].children) == 1
		assert len(graphics[1].inputs[0].children) == 1
		assert len(graphics[2].inputs[0].children) == 0

	def test_ConstructMultipleOutputsTree(self):
		tookitMock = Mock()
		tookitMock.GetTypePixmap = Mock(return_value=QPixmap())

		graphics = []
		graphics.append(ProcessGraphic(ProductionProcess(DummyBlueprint([3, 4], 5)), tookitMock))
		graphics.append(ProcessGraphic(ProductionProcess(DummyRefine(2, [3])), tookitMock))
		graphics.append(ProcessGraphic(ProductionProcess(DummyRefine(1, [3, 4])), tookitMock))

		ConstructProcessGraphicTree(graphics)

		assert len(graphics[0].inputs[0].children) == 2
		assert len(graphics[0].inputs[1].children) == 1
		assert len(graphics[1].inputs[0].children) == 0
		assert len(graphics[2].inputs[0].children) == 0


class ItemStackGraphic(QGraphicsItem):
	def __init__(self, aItemStack, aParent, aPos, aToolkitTypes):
		super().__init__(aParent)
		self.setPos(aPos)
		self.itemStack = aItemStack
		self.rect = QRectF(-35, 0, 70, 35)
		self.children = []
		icon = QGraphicsPixmapItem(aToolkitTypes.GetTypePixmap(self.itemStack.itemId, 32), self)
		icon.setPos(QPointF(-33, 2))

	def paint(self, painter, option, widget=None):
		painter.fillRect(self.rect, Qt.white)
		painter.drawRect(self.rect)
		painter.drawText(self.rect, Qt.AlignVCenter + Qt.AlignRight, str(self.itemStack.ammount))

	def GetInScenePos(self):
		return self.scenePos() + QPointF(-35, 17)

	def GetOutScenePos(self):
		return self.scenePos() + QPointF(35, 17)

	def boundingRect(self):
		return self.rect
	
	def GetItemId(self):
		return self.itemStack.itemId

class ProcessGraphic(QGraphicsItem):
	def __init__(self, aProductionProcess, aToolkitTypes):
		super().__init__()
		self.process = aProductionProcess
		self.col = 0
		self.row = 0
		self.inputs = []
		self.outputs = []

		icon = QGraphicsPixmapItem(aToolkitTypes.GetTypePixmap(self.process.scheme.schemeId, 32), self)
		
		width = 160
		space = 40

		inputOffset = 0
		outputOffset = 0

		for inp in self.process.scheme.GetInputs():
			inputOffset = inputOffset + space
			self.inputs.append(ItemStackGraphic(inp, self, QPointF(0, inputOffset), aToolkitTypes))

		for out in self.process.scheme.GetOutputs():
			outputOffset = outputOffset + space
			self.outputs.append(ItemStackGraphic(out, self, QPointF(width, outputOffset), aToolkitTypes))

		self.rect = QRectF(0, 0, width, max(outputOffset, inputOffset) + space)
		
		spinbox = QSpinBox()
		spinbox.setRange(1, 1000000000)
		proxy = QGraphicsProxyWidget(self)
		proxy.setWidget(spinbox)		
		proxy.setPos(QPointF(width / 2 - spinbox.width() / 2, 10))


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
		painter.drawText(self.rect, Qt.AlignHCenter + Qt.AlignVCenter, self.process.scheme.GetName())

	def boundingRect(self):
		return self.rect

def ConstructProcessGraphicTree(graphics):

	outputsByItemId = {}
	for graphic in graphics:
		for out in graphic.outputs:
			outputsByItemId.setdefault(out.GetItemId(), []).append(out)
	
	for parentProcess in graphics:
		for inp in parentProcess.inputs:
			if inp.GetItemId() in outputsByItemId:
				outputs = outputsByItemId[inp.GetItemId()]
				for out in outputs:
					inp.children.append(out)


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

	colWidth = 400
	rowHeigth = 360
	border = 50
	sceneWidth = colWidth * maxCol + border * 2
	sceneHeight = rowHeigth * maxRow + border * 2
	aScene.setSceneRect(QRectF(0, 0, sceneWidth, sceneHeight))
	aScene.clear()

	## Set process positions
	for graphic in aGraphics:
		x = 50 + sceneWidth - (graphic.col + 1) * colWidth
		y = 50 + graphic.row * rowHeigth
		graphic.setPos(QPointF(x, y))
		aScene.addItem(graphic)

	## Add lines
	for graphic in aGraphics:
		for inp in graphic.inputs:
			for child in inp.children:
				controlOffset = 100
				start = child.GetOutScenePos()
				control1 = start + QPointF(controlOffset, 0)
				end = inp.GetInScenePos()
				control2 = end + QPointF(-controlOffset, 0)

				path = QPainterPath()
				path.moveTo(start)
				path.cubicTo(control1, control2, end)

				line = QGraphicsPathItem(path)
				line.setZValue(-1000)
				aScene.addItem(line)

