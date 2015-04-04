

from PyQt5.QtCore import QPointF, QRect, QRectF, QSize, QSizeF, Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtGui import QFontMetricsF, QFont

class InputGraphic(QGraphicsItem):
	def __init__(self, aItemStack, aParent, aPos, aToolkitTypes):
		super().__init__(aParent)
		self.setPos(aPos)
		self.itemStack = aItemStack
		self.font = QFont()
		icon = QGraphicsPixmapItem(aToolkitTypes.GetTypePixmap(self.itemStack.itemId, 32), self)
		icon.setPos(QPointF(2, 2))

	def paint(self, painter, option, widget=None):
		rect = self.boundingRect()
		painter.drawText(rect, Qt.AlignVCenter + Qt.AlignRight, str(self.itemStack.ammount))

	def GetScenePos(self):
		return self.scenePos() + QPointF(0, 17)

	def boundingRect(self):
		fm = QFontMetricsF(self.font)
		width = 32 + fm.width(str(self.itemStack.ammount))
		return QRectF(0, 0, width, 35)
	
	def GetItemId(self):
		return self.itemStack.itemId

class OutputGraphic(QGraphicsItem):
	def __init__(self, aItemStack, aParent, aPos, aToolkitTypes):
		super().__init__(aParent)
		self.setPos(aPos)
		self.itemStack = aItemStack
		self.font = QFont()
		icon = QGraphicsPixmapItem(aToolkitTypes.GetTypePixmap(self.itemStack.itemId, 32), self)
		icon.setPos(QPointF(-34, 2))

	def GetWidth(self):
		fm = QFontMetricsF(self.font)
		return 32 + fm.width(str(self.itemStack.ammount))


	def paint(self, painter, option, widget=None):
		width = self.GetWidth()
		rect = QRectF(-width, 0, width - 34, 35)
		painter.drawText(rect, Qt.AlignVCenter + Qt.AlignRight, str(self.itemStack.ammount))

	def GetScenePos(self):
		return self.scenePos() + QPointF(-self.GetWidth(), 17)

	def boundingRect(self):
		width = self.GetWidth()
		return QRectF(-width, 0, width, 35)
	
	def GetItemId(self):
		return self.itemStack.itemId