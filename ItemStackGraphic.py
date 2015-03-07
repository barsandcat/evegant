

from PyQt5.QtCore import QPointF, QRect, QRectF, QSize, QSizeF, Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem

class ItemStackGraphic(QGraphicsItem):
	def __init__(self, aItemStack, aParent, aPos, aToolkitTypes):
		super().__init__(aParent)
		self.setPos(aPos)
		self.itemStack = aItemStack
		self.rect = QRectF(-35, 0, 70, 35)
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