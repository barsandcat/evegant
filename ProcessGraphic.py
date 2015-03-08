

from ItemStackGraphic import ItemStackGraphic

from PyQt5.QtCore import QPointF, QRectF, QSizeF, Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsProxyWidget, QSpinBox


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

		for inp in self.process.inputs:
			inputOffset = inputOffset + space
			self.inputs.append(ItemStackGraphic(inp, self, QPointF(0, inputOffset), aToolkitTypes))

		for out in self.process.outputs:
			outputOffset = outputOffset + space
			self.outputs.append(ItemStackGraphic(out, self, QPointF(width, outputOffset), aToolkitTypes))

		self.rect = QRectF(0, 0, width, max(outputOffset, inputOffset) + space)
		
		spinbox = QSpinBox()
		spinbox.setRange(1, 1000000000)
		spinbox.valueChanged.connect(self.OnRunChanged)
		proxy = QGraphicsProxyWidget(self)
		proxy.setWidget(spinbox)		
		proxy.setPos(QPointF(width / 2 - spinbox.width() / 2, 10))

	def OnRunChanged(self, value):
		self.process.SetRuns(value)
		self.update()
		for inp in self.inputs:
			inp.update()
		for out in self.outputs:
			out.update()


	def paint(self, painter, option, widget=None):
		painter.fillRect(self.rect, Qt.white)
		painter.drawRoundedRect(self.rect, 10, 10)
		painter.drawText(self.rect, Qt.AlignHCenter + Qt.AlignVCenter, self.process.scheme.GetName())

	def boundingRect(self):
		return self.rect