import json
from pprint import pprint

config = {}

def init_config():
    global config
    # load current inputs model
    with open('config.json') as data_file:
		config = json.loads(data_file.read())
		pprint(config)

def get_config():
    return config
