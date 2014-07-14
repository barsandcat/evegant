
import yaml

class ToolkitBlueprints:
	def __init__(self):
		file = open('Eve toolkit/blueprints.yaml')
		self.blueprints = yaml.load(file)
