import zipfile
from PyQt5.QtGui import QPixmap


class ToolkitTypes:
	def __init__(self):
		self.archive = zipfile.ZipFile('Eve toolkit/Rubicon_1.3_Types.zip')

	def Close(self):
		self.archive.close()

	def GetTypePixmap(self, aTypeId, aSize):
		pixmap = QPixmap()
		filename = 'Types/{0}_{1}.png'.format(aTypeId, aSize)
		pixmap.loadFromData(self.archive.read(filename))
		return pixmap

