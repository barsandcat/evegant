
import sqlite3


import unittest
from unittest.mock import (Mock, MagicMock)

from logging import (info, warning, error)

class TestEveDB(unittest.TestCase):

	def test_LoadBlueprint(self):
		cursor = Mock()
		cursor.fetchall = Mock(return_value = [(34, 2730), (35, 214), (36, 303), (37, 4), (38, 2), (39, 2)])
		cursor.fetchone = Mock(return_value = (939, 592, 'Navitas Blueprint'))
		bp = LoadBlueprint(cursor, 939)
		self.assertEqual(len(bp.GetOutputs()), 1)
		self.assertEqual(len(bp.GetInputs()), 6)


class BluePrint:
	def __init__(self, aId, aName, aInputs, aOutput):
		self.schemaId = aId
		self.name = aName
		self.inputs = aInputs
		self.output = aOutput

	def GetOutputs(self):
		return [self.output]

	def GetInputs(self):
		return self.inputs

	def GetName(self):
		return self.name


def LoadBlueprint(aCursor, aBlueprintId):
	
	aCursor.execute("SELECT tm.materialTypeID, quantity "
		"FROM invTypeMaterials tm, invBlueprintTypes bt "
		"WHERE tm.typeID = bt.productTypeID "
		"AND bt.blueprintTypeID = ?", (aBlueprintId,))
	rows = aCursor.fetchall()

	inputs = [row[0] for row in rows]
	aCursor.execute("SELECT blueprintTypeID, productTypeID, typeName "
		"FROM invBlueprintTypes bt, invTypes t "
		"WHERE blueprintTypeID = ? "
		"AND bt.blueprintTypeID = t.typeID;", (aBlueprintId,))
	row = aCursor.fetchone()

	return BluePrint(row[0], row[2], inputs, row[1])
	
