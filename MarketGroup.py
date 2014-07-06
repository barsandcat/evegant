
from EveDB import BluePrint, LoadBlueprint, Refine, LoadRefine

class MarketGroup:
	def __init__(self, aName, aParent=None):
		self.parent = aParent
		self.name = aName
		self.children = []

	def AppendChild(self, aItem):
		self.children.append(aItem)

	def SetParent(self, aParent):
		self.parent = aParent

	def GetChild(self, row):
		return self.children[row]

	def GetChildCount(self):
		return len(self.children)

	def GetIndexOfChild(self, aChild):
		return self.children.index(aChild)

	def GetName(self):
		return self.name

	def GetParent(self):
		return self.parent


class LazyMarketGroup:
	def __init__(self, aMarketGroupId, aName, aParent, aDBConnection):
		self.parent = aParent
		self.name = aName
		self.children = None
		self.marketGroupId = aMarketGroupId
		self.db = aDBConnection

	def CacheChildren(self):
		if self.children == None:
			self.children = []
			cursor = self.db.cursor()
			#Load child market groups
			cursor.execute("SELECT marketGroupID, marketGroupName "
				"FROM invMarketGroups WHERE parentGroupID = ?", 
				(self.marketGroupId,))			
			
			for row in cursor:
				marketGroupId = row[0]
				name = row[1]
				self.children.append(LazyMarketGroup(marketGroupId, name, self, self.db))

			#Load child types, if it is blueprint - should have not null blueprintID
			cursor.execute("SELECT typeID, blueprintTypeID "
				"FROM invTypes LEFT JOIN invBlueprintTypes ON typeID = blueprintTypeID "
				"WHERE marketGroupID = ?", (self.marketGroupId,))

			for row in cursor:
				if row[1]:
					blueprint = LoadBlueprint(self.db.cursor(), row[1], self)
					self.children.append(blueprint)
				else:
					refine = LoadRefine(self.db.cursor(), row[0], self)
					self.children.append(refine)


	def GetChild(self, row):
		self.CacheChildren()
		return self.children[row]

	def GetChildCount(self):
		self.CacheChildren()
		return len(self.children)

	def GetIndexOfChild(self, aChild):
		self.CacheChildren()
		return self.children.index(aChild)

	def GetName(self):
		return self.name

	def GetParent(self):
		return self.parent

