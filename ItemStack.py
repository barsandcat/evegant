
class ItemStack:
	def __init__(self, aItemId, aAmmount):
		self.itemId = aItemId
		self.ammount = aAmmount
	def __str__(self):
		return str(self.itemId) + ": " + str(self.ammount)