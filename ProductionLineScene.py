
from ProductionLine import ProductionLine
from ProductionProcess import ProductionProcess
from Schemes import Blueprint, Refine
from ItemStack import ItemStack
from ProcessGraphic import ProcessGraphic

from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
		QSizeF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
		QPainterPath, QPen, QPixmap, QPolygonF)
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsPixmapItem, QGraphicsPathItem, QGraphicsScene, QGraphicsProxyWidget, QSpinBox


from unittest import TestCase
from unittest.mock import Mock

from logging import warning, error, info

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

		GetProcessGraphicPositions(graphics)

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

		GetProcessGraphicPositions(graphics)

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

		GetProcessGraphicPositions(graphics)

		assert len(graphics[0].inputs[0].children) == 2
		assert len(graphics[0].inputs[1].children) == 1
		assert len(graphics[1].inputs[0].children) == 0
		assert len(graphics[2].inputs[0].children) == 0

def GetProcessGraphicPositions(processGraphics):

	outputsByItemId = {}
	for processGraphic in processGraphics:
		for outGraphic in processGraphic.outputs:
			outputsByItemId.setdefault(outGraphic.GetItemId(), []).append(outGraphic)
	
	for parentProcess in processGraphics:
		for inpGraphic in parentProcess.inputs:
			if inpGraphic.GetItemId() in outputsByItemId:
				outputs = outputsByItemId[inpGraphic.GetItemId()]
				for outGraphic in outputs:
					inpGraphic.children.append(outGraphic)

					
					
def GetChildrenProcesses(aProcessGraphic):
	children = set()
	for inp in aProcessGraphic.inputs:
		for childOut in inp.children:
			childProcess = childOut.parentItem()
			children.add(childProcess)

	return children

def FillScene(aScene, aProcessGraphics):	
	## Findout process column
	queue = [aProcessGraphics[0]]
	done = set()
	while queue:
		graphic = queue.pop(0)
		if graphic not in done:
			done.add(graphic)
			children = GetChildrenProcesses(graphic)
			for child in children:
				child.col = max(child.col, graphic.col + 1)
				queue.append(child)
	

	## Findout process row
	processRows = {}
	for graphic in aProcessGraphics:
		graphic.row = processRows.get(graphic.col, 0)
		processRows[graphic.col] = graphic.row + 1
		
	maxRow = 0
	maxCol = 0
	for graphic in aProcessGraphics:
		maxRow = max(maxRow, graphic.row)
		maxCol = max(maxCol, graphic.col)
	maxRow = maxRow + 1
	maxCol = maxCol + 1
	
	colWidth = 400
	rowHeigth = 360
	border = 50

	sceneWidth = colWidth * maxCol + border * 2
	sceneHeight = rowHeigth * maxRow + border * 2
	aScene.setSceneRect(QRectF(0, 0, sceneWidth, sceneHeight))
	aScene.clear()

	## Set process positions
	for graphic in aProcessGraphics:
		x = 50 + sceneWidth - (graphic.col + 1) * colWidth
		y = 50 + graphic.row * rowHeigth
		graphic.setPos(QPointF(x, y))
		aScene.addItem(graphic)

		
	## Add lines
	for graphic in aProcessGraphics:
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

