

from ItemStackGraphic import InputGraphic, OutputGraphic

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
		icon.setPos(2, 2)
		
		width = 160
		space = 40

		inputOffset = 40
		outputOffset = 40

		for inp in self.process.inputs:
			inputOffset = inputOffset + space
			self.inputs.append(InputGraphic(inp, self, QPointF(0, inputOffset), aToolkitTypes))

		for out in self.process.outputs:
			outputOffset = outputOffset + space
			self.outputs.append(OutputGraphic(out, self, QPointF(width, outputOffset), aToolkitTypes))

		self.rect = QRectF(0, 0, width, max(outputOffset, inputOffset) + space)
		
		spinbox = QSpinBox()
		spinbox.setRange(1, 1000000000)
		spinbox.setValue(self.process.runs)
		spinbox.valueChanged.connect(self.OnRunChanged)

		proxy = QGraphicsProxyWidget(self)
		proxy.setWidget(spinbox)		
		proxy.setPos(QPointF(width / 2 - spinbox.width() / 2, 40))
		self.runs = proxy
		self.spinbox = spinbox

	def OnRunChanged(self, value):
		self.process.SetRuns(value)
		self.update()
		self.runs.update()

		for inp in self.inputs:
			inp.update()
		for out in self.outputs:
			out.update()


	def paint(self, painter, option, widget=None):
		if not self.process.manual:
			self.spinbox.setValue(self.process.runs)


		painter.fillRect(self.rect, Qt.white)
		painter.drawRect(self.rect)

		painter.drawText(QPointF(40, 30), self.process.scheme.GetName())

	def boundingRect(self):
		return self.rect