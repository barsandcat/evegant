
import yaml

def LoadBlueprints():
	file = open('Eve toolkit/blueprints.yaml')
	return yaml.load(file)
