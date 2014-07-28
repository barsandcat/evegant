import os
import pickle

import yaml

cacheFileName = 'blueprints.cache'

def LoadBlueprints():

	if os.path.isfile(cacheFileName):
		cache = open(cacheFileName, 'rb')
		blueprints = pickle.load(cache)
		cache.close()
	else:
		file = open('Eve toolkit/blueprints.yaml')
		blueprints = yaml.load(file)
		file.close()
		
		cache = open(cacheFileName, 'wb')
		pickle.dump(blueprints, cache)
		cache.close()   

	return blueprints
