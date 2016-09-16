
# configs.py	:	Configs management module

import client
import tools

def get_configs_list(screen_id):
	configs = []
	cmd = "ConfigList()"
	result = client.corio_send_command(screen_id, cmd)  # result "Configs.Config1 = <...>\r\nConfigs.Config2 = <...>\r\nConfigs.Config3...\r\n"
	configs = tools.convertTVONEListToJsonList(result, True, True)
	return configs
	
def get_config(screen_id, config_id):
	cmd = 'Configs.Config{0}'.format( config_id )
	result = client.corio_send_command(screen_id, cmd) 
	result = tools.convertTVONEListToJsonList(result)
	return result
	
def save_config(screen_id, config_id):
	cmd = 'Configs.Config{0}.Backup()'.format( config_id )
	client.corio_send_command(screen_id, cmd) 
	
def get_current_config_name(screen_id):
	cmd = "System.ConfigName"
	result = client.corio_send_command(screen_id, cmd) 
	name = tools.getTVONEValue(result)
	if not (name==""):
		return name
	return "unknown..."

def load_config(screen_id, config_id):
	cmd = 'Configs.Config{0}.Restore()'.format( config_id )
	client.corio_send_command(screen_id, cmd) 
	
def delete_config(screen_id, config_id):
	cmd = 'Configs.Config{0}.Remove()'.format( config_id )
	client.corio_send_command(screen_id, cmd) 
	