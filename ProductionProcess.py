
class ProductionProcess:
	def __init__(self, aScheme):
		self.scheme = aScheme
		self.runs = 1

	def SetRuns(self, aRuns):
		self.runs = aRuns
