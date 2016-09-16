
# content.py	:	Content management module

import client
import tools
import windows

def set_content_crop_left(screen_id, slot, input_id, amount):
    cmd = 'Slot{0}.In{1}.LeftCrop = {2}'.format( slot, input_id, amount)
    client.corio_send_command(screen_id, cmd)

def set_content_crop_right(screen_id, slot, input_id, amount):
    cmd = 'Slot{0}.In{1}.RightCrop = {2}'.format( slot, input_id, amount)
    client.corio_send_command(screen_id, cmd)

def set_content_crop_top(screen_id, slot, input_id, amount):
    cmd = 'Slot{0}.In{1}.TopCrop = {2}'.format( slot, input_id, amount)
    client.corio_send_command(screen_id, cmd)

def set_content_crop_bottom(screen_id, slot, input_id, amount):
    cmd = 'Slot{0}.In{1}.BottomCrop = {2}'.format( slot, input_id, amount)
    client.corio_send_command(screen_id, cmd)

def set_content_resolution(screen_id, slot, input_id, resolution):
    cmd = 'Slot{0}.In{1}.Resolution = {2}'.format( slot, input_id, resolution)
    client.corio_send_command(screen_id, cmd)

def get_content_resolution(screen_id, slot, input_id):
    cmd = 'Slot{0}.In{1}.Set_Resolution'.format( slot, input_id)
    result = client.corio_send_command(screen_id, cmd)	# receive something as "Slot14.Out1.Width = 1920 \n!Done Slot14.Out1.Width"
    set_res = tools.getTVONEValue(result)
    cmd = 'Slot{0}.In{1}.Measured_Resolution'.format( slot, input_id)
    result = client.corio_send_command(screen_id, cmd)	# receive something as "Slot14.Out1.Width = 1920 \n!Done Slot14.Out1.Width"
    mes_res = tools.getTVONEValue(result)
    #val = [int(s) for s in result.split() if s.isdigit()]
    #width = val[0]
    #cmd = 'Slot{0}.In{1}.Height'.format( slot, input_id)
    #result = client.corio_send_command(screen_id, cmd)
    #val = [int(s) for s in result.split() if s.isdigit()]
    #height = val[0]
    #cmd = 'Slot{0}.In{1}.Field_Rate'.format( slot, input_id)
    #result = client.corio_send_command(screen_id, cmd)
    #val = [int(s) for s in result.split() if s.isdigit()]
    #fps = val[0]
    return {'set': set_res, 'measured': mes_res};
	
def play_content(screen_id, slot, input_id, uri):
    input = "127.0.0.1:8080"
    url = "http://" + input + "/requests/status.xml?command=in_play&input=" + uri
    r = requests.get(url, auth=('', 'toto'))

def stop_content(screen_id, slot, input_id):
    input = "127.0.0.1:8080"
    url = "http://" + input + "/requests/status.xml?command=pl_stop"
    r = requests.get(url, auth=('', 'toto'))

def set_content_crop(screen_id, window_id, l, r, t, b):
    slot_id, input_id = windows.get_window_input(screen_id, window_id)
    self.set_content_crop_left(screen_id, slot_id, input_id, l)
    self.set_content_crop_left(screen_id, slot_id, input_id, r)
    self.set_content_crop_left(screen_id, slot_id, input_id, t)
    self.set_content_crop_left(screen_id, slot_id, input_id, b)
