

from PyQt5.QtCore import QPointF, QRect, QRectF, QSize, QSizeF, Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtGui import QFontMetricsF, QFont

class ItemStackGraphic(QGraphicsItem):
	def __init__(self, aItemStack, aParent, aPos, aToolkitTypes):
		super().__init__(aParent)
		self.setPos(aPos)
		self.itemStack = aItemStack
		self.font = QFont()
		icon = QGraphicsPixmapItem(aToolkitTypes.GetTypePixmap(self.itemStack.itemId, 32), self)
		icon.setPos(QPointF(-33, 2))

	def paint(self, painter, option, widget=None):
		rect = self.boundingRect()
		painter.fillRect(rect, Qt.white)
		painter.drawRect(rect)
		painter.drawText(rect, Qt.AlignVCenter + Qt.AlignRight, str(self.itemStack.ammount))

	def GetInScenePos(self):
		return self.scenePos() + QPointF(-35, 17)

	def GetOutScenePos(self):
		return self.scenePos() + QPointF(35, 17)

	def boundingRect(self):
		fm = QFontMetricsF(self.font)
		width = 32 + fm.width(str(self.itemStack.ammount))
		return QRectF(-35, 0, width, 35)
	
	def GetItemId(self):
		return self.itemStack.itemId