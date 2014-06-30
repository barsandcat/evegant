
import sqlite3


import unittest
import unittest.mock

class TestEveDB(unittest.TestCase):

	def test_LoadBlueprint(self):
		bp = LoadBluprint(939)


dbFileName = "Eve toolkit/DATADUMP201403101147.db"


class BluePrint:
	def __init__(self, aId, aName, aInputs, aOutputs):
		self.schemeId = aId
		self.name = aName
		self.inputs = aInputs
		self.aOutputs = aOutputs

	def GetName():
		return name


def LoadBluprint(aBlueprintId):
	connection = sqlite3.connect(dbFileName)
	bp = None
	
	with connection:
		connection.row_factory = sqlite3.Row

		cursor = connection.cursor()
		cursor.execute("SELECT blueprintTypeID, productTypeID, typeName "
			"FROM invBlueprintTypes bt, invTypes t "
			"WHERE blueprintTypeID = ? "
			"AND bt.blueprintTypeID = t.typeID;", (aBlueprintId,))
		row = cursor.fetchone()
		bp = BluePrint(row["blueprintTypeID"], row["typeName"], [], [row["productTypeID"]])

		assert cursor.fetchone() == None
	
	return bp

