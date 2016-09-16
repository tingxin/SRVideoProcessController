
# presets.py	:	Presets management module

import client
import tools
import windows

def get_presets_list(screen_id):
    # Get the presets list
    presets = []
    cmd = 'Preset.PresetList()'
    result = client.corio_send_command(screen_id, cmd)	# receive list 'Routing.Preset.PresetList[1]=Background,Canvas1,1000\r\nRouting.Preset.PresetList[2]=Movie,Canvas1,0\r\nRouting.Preset.PresetList[3]=Monitoring_All_SRC,Canvas4,0\r\nRouting.Preset.PresetList[4]=Monitoring_One_SRC,Canvas4,0\r\nRouting.Preset.PresetList[5]=CL,Canvas1,3000\r\nRouting.Preset.PresetList[6]=Whiteboard,Canvas1,1000\r\nRouting.Preset.PresetList[7]=Control_Room_slides,Canvas1,1000\r\n!Done '
    presets = tools.convertTVONEListToJsonList(result, True, True)
    # split response in multiline
    #presetList = result.split('\n')
    # then get the list of presets number
    #for preset in presetList:
    #	tokens = preset.split('=')
    #	if( len(tokens) > 1 ):
    #		tab = re.findall(r'\d+', tokens[0])
    #		presets.append( {tab[0]:tokens[1]} )
    return presets

def get_active_preset(screen_id):
    cmd = 'Preset.Take'
    result = client.corio_send_command(screen_id, cmd)
    val = [int(s) for s in result.split() if s.isdigit()]
    return val[0]

def set_active_preset(screen_id, preset_id):
    cmd = 'Preset.Take = {0}'.format( preset_id)
    client.corio_send_command(screen_id, cmd)
    windows.refresh_window_canvas(screen_id)

def get_editable_preset(screen_id):
    cmd = 'Preset.Read'
    result = client.corio_send_command(screen_id, cmd)
    val = [int(s) for s in result.split() if s.isdigit()]
    return val[0]

def set_editable_preset(screen_id, preset_id):
    cmd = 'Preset.Read = {0}'.format( preset_id)
    client.corio_send_command(screen_id, cmd)

def save_active_preset(screen_id):
    cmd = 'Preset.SaveRead()'
    client.corio_send_command(screen_id, cmd)

def rename_active_preset(screen_id, name):
    cmd = 'Preset.NameRead = {0}'.format( name)
    client.corio_send_command(screen_id, cmd)

def delete_active_preset(screen_id):
    cmd = 'Preset.RmvPresetFileRead()'
    client.corio_send_command(screen_id, cmd)

def create_preset(screen_id, preset_id, name):
    cmd = 'Preset.Read = {0}'.format( preset_id)
    client.corio_send_command(screen_id, cmd)
    cmd = 'Preset.NameRead = {0}'.format( name)
    client.corio_send_command(screen_id, cmd)
    cmd = 'Preset.DurationRead = {0}'.format( 0 )
    client.corio_send_command(screen_id, cmd)
    cmd = 'Preset.CanvasRead = {0}'.format( 'Canvas1' )
    client.corio_send_command(screen_id, cmd)
    cmd = 'Preset.SaveRead()'
    client.corio_send_command(screen_id, cmd)
