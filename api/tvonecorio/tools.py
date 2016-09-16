
# Tools module

import re
from pprint import pprint

# convertTVONEListToJson(): convert a TVOne list as "Configs.Config1 = <...>\r\nConfigs.Config2 = <...>\r\nConfigs.Config3...\r\n" to
# json object as
def convertTVONEListToJsonList(response, remove_prefix=True, extract_id=False):
	list = {}	# type dictionaries
	lines = response.split('\r\n')
	for line in lines:
		tokens = line.split('=')
		if len( tokens ) > 1 :
			tokens[0] = tokens[0].strip()
			tokens[1] = tokens[1].strip()
			if remove_prefix :
				start_pos = tokens[0].rfind(".") + 1
				tokens[0] = tokens[0][start_pos:]
			if extract_id :
				subs = re.findall(r'\d+', tokens[0])
				if len(subs) > 0 :
					tokens[0] = subs[0]
			list[ tokens[0] ] = tokens[1]
	return list

def convertTVONEListToJsonArray(tvone_list, remove_prefix=True, extract_id=False):
	array = []
	lines = tvone_list.split('\n')
	for line in lines:
		values = line.split('=')
		if len( values ) > 1 :
			values[0] = values[0].strip()
			values[1] = values[1].strip()
			if remove_prefix :
				start_pos = values[0].rfind(".") + 1
				values[0] = values[0][start_pos:]
			if extract_id :
				tokens = re.findall(r'\d+', values[0])
				if len(tokens) > 0 :
					values[0] = tokens[0]
			array.append( { values[0]: values[1] } )
	return array

def getTVOneParameter( response ):
	dict = convertTVONEListToJsonList(response, False, False)
	if len( dict.keys() ) != 1:
		print "getTVOneParameter(): warn, expect one parameter, "+len( dict.keys() )+" detected!"
	for key in dict.keys():
		return dict[key]
	#error
	print "getTVOneParameter(): unexpected error"

def getTVONEValue(parameter):
	value = ""
	tokens = parameter.split('=')
	if( len(tokens) > 0 ):
		value = tokens[1].strip()
		tokens = value.split('\r\n')
		return tokens[0].strip()
	return ""

# convert someting like "Slot2.In1" to "s2.i1"
def getMinSourceName( name ):
	min_name = ""
	tokens = name.split('.')
	if len(tokens) == 2 :
		slot_id = re.findall(r'\d+', tokens[0])
		input_id = re.findall(r'\d+', tokens[1])

		if tokens[1].startswith('In'):
			min_name = 's{0}.i{1}'.format( slot_id[0], input_id[0])
		elif tokens[1].startswith('Out'):
			min_name = 's{0}.o{1}'.format( slot_id[0], input_id[0])
	#print "min_name="+min_name

	return min_name
