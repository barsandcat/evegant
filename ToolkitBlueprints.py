
import yaml

def LoadBlueprints(self):
	file = open('Eve toolkit/blueprints.yaml')
	return yaml.load(file)
