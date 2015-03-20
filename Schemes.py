
import sqlite3
import yaml

from unittest import TestCase
from unittest.mock import Mock, MagicMock
from logging import info, warning, error

from ItemStack import ItemStack

class TestEveDB(TestCase):

	def test_YamlToBlueprint(self):
		blueprints = yaml.load(
'''
681:
  activities:
    1:
      materials:
        38:
          quantity: 86
      products:
        165:
          quantity: 1
      time: 600
    3:
      time: 210
    4:
      time: 210
    5:
      time: 480
  blueprintTypeID: 681
  maxProductionLimit: 300'''
		)
		
		
		bp = YamlToBlueprint(blueprints[681], "", None)
		self.assertEqual(bp.GetOutputs()[0].itemId, 165)
		self.assertEqual(bp.GetInputs()[0].itemId, 38)

		
def CreateSchemesTree(aConnection, aBlueprints):
	treeRoot = MarketGroup("Type")
	cursor = aConnection.cursor()
	cursor.execute("SELECT marketGroupID, parentGroupID, marketGroupName FROM invMarketGroups")
	marketGroups = {}
	for row in cursor:
		groupID = row[0]
		parentID = row[1]
		groupName = row[2]
		marketGroups[groupID] = MarketGroup(groupName, parentID)
	
	for key, child in marketGroups.items():
		parentID = child.GetParent()
		if parentID:
			parent = marketGroups[parentID]
		else:
			parent = treeRoot
		child.SetParent(parent)
		parent.AppendChild(child)
		
	cursor.execute("SELECT t.typeID, c.categoryID, t.marketGroupID, t.typeName FROM invTypes t, invGroups g, invCategories c WHERE t.groupID = g.groupID AND g.categoryID = c.categoryID ORDER BY t.typeID")

	for row in cursor:
		groupId = row[2]
		if groupId and groupId in marketGroups:
			group = marketGroups[groupId]
			categoryId = row[1]
			name = row[3]
			typeId = row[0]
			if categoryId == 9:
				child = YamlToBlueprint(aBlueprints[typeId], name, group)
				group.AppendChild(child)
			if categoryId == 25:
				child = LoadRefine(aConnection.cursor(), typeId, group)
				group.AppendChild(child)
			


	return treeRoot

class Blueprint:
	def __init__(self, aId, aName, aGroup, aInputs, aOutput):
		self.schemeId = aId
		self.name = aName
		self.inputs = aInputs
		self.output = aOutput
		self.group = aGroup

	def GetOutputs(self):
		return [self.output]

	def GetInputs(self):
		return self.inputs

	def GetName(self):
		return self.name

	def GetChild(self, row):
		return None

	def GetChildCount(self):
		return 0

	def GetIndexOfChild(self, aChild):
		return 0

	def GetParent(self):
		return self.group


class Refine:
	def __init__(self, aId, aName, aGroup, aInput, aOutputs):
		self.schemeId = aId
		self.name = aName
		self.input = aInput
		self.outputs = aOutputs
		self.group = aGroup

	def GetOutputs(self):
		return self.outputs

	def GetInputs(self):
		return [self.input]

	def GetName(self):
		return self.name

	def GetChild(self, row):
		return None

	def GetChildCount(self):
		return 0

	def GetIndexOfChild(self, aChild):
		return 0

	def GetParent(self):
		return self.group

def LoadRefine(aCursor, aTypeId, aGroup):
	
	aCursor.execute("SELECT materialTypeID, quantity "
		"FROM invTypeMaterials "
		"WHERE typeID = ? ",	(aTypeId,))
	rows = aCursor.fetchall()

	outputs = [ItemStack(row[0], row[1]) for row in rows]

	aCursor.execute("SELECT typeName "
		"FROM invTypes t "
		"WHERE typeID = ? ", (aTypeId,))
	row = aCursor.fetchone()

	return Refine(aTypeId, row[0], aGroup, ItemStack(aTypeId, 100), outputs)
	
def YamlToBlueprint(aBlueprint, aName, aGroup):
	manufacturing = aBlueprint["activities"][1]
	blueprintId = aBlueprint["blueprintTypeID"]
	inputs = []
	for id, params in manufacturing["materials"].items():
		inputs.append(ItemStack(id, params["quantity"]))
		
	outputs = []
	for id, params in manufacturing["products"].items():
		outputs.append(ItemStack(id, params["quantity"]))		
	
	return Blueprint(blueprintId, aName, aGroup, inputs, outputs[0])
	
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

	def GetOutputs(self):
		return []
		
	def GetInputs(self):
		return []

def SchemeToStr(aScheme):
	inputs = ""
	for inp in aScheme.GetInputs():
		inputs += str(inp)
		inputs += "\n"
	outputs = ""
	for out in aScheme.GetOutputs():
		outputs += str(out)
		outputs += "\n"
	
	return aScheme.GetName() + ":\nInputs:\n" + inputs + "Outputs:\n" + outputs