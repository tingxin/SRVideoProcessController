
# windows.py	:	Windows management module

import client
import tools
import contents
import slots

import re

def get_windows_list(screen_id):
    windows = []
    cmd = 'Windows'
    result = client.corio_send_command(screen_id, cmd)  # result "Windows.Window1 = <...>\r\nWindows.Window2 = <...>\r\nWindows.Window3 = <...>\r\nWindows.Window4 = <...>\r\n"
    windows = tools.convertTVONEListToJsonList(result, True, True)
    # retrieve all windows name
    for key in windows.keys():
        #print key, ": ", window[key]
        name = get_windows_name( screen_id, key )
        windows[key] = name
    return windows

def get_windows_name(screen_id, window_id):
    # First take Alias if it's available (i.e value is not "NULL")
    cmd = 'Window{0}.Alias'.format(window_id)
    result = client.corio_send_command(screen_id, cmd)
    name = tools.getTVONEValue(result);
    if name == "NULL":
        cmd = 'Window{0}.FullName'.format(window_id)
        result = client.corio_send_command(screen_id, cmd)
        name = tools.getTVONEValue(result);
    return name

def get_window(screen_id, window_id):
    result = {}
    cmd = 'Window{0}'.format( window_id )
    result = client.corio_send_command(screen_id, cmd)
    result = tools.convertTVONEListToJsonList(result)
    return result

def set_window_width(screen_id, window_id, w):
    cmd = 'Windows.window{0}.CanWidth = {1}'.format( window_id, w)
    client.corio_send_command(screen_id, cmd)

def get_window_width(screen_id, window_id):
    cmd = 'Windows.window{0}.CanWidth'.format( window_id )
    result = client.corio_send_command(screen_id, cmd)
    value = tools.getTVOneParameter( result )
    return int(value)

def set_window_height(screen_id, window_id, h):
    cmd = 'Windows.window{0}.CanHeight = {1}'.format( window_id, h)
    client.corio_send_command(screen_id, cmd)

def get_window_height(screen_id, window_id):
    cmd = 'Windows.window{0}.CanHeight'.format( window_id )
    result = client.corio_send_command(screen_id, cmd)
    value = tools.getTVOneParameter( result )
    return int(value)

def set_window_x_position(screen_id, window_id, x):
    cmd = 'Windows.window{0}.CanXCentre = {1}'.format( window_id, x)
    client.corio_send_command(screen_id, cmd)

def get_window_x_position(screen_id, window_id):
    cmd = 'Windows.window{0}.CanXCentre'.format( window_id )
    result = client.corio_send_command(screen_id, cmd)
    value = tools.getTVOneParameter( result )
    return int(value)

def set_window_y_position(screen_id, window_id, y):
    cmd = 'Windows.window{0}.CanYCentre = {1}'.format( window_id, y)
    client.corio_send_command(screen_id, cmd)

def get_window_y_position(screen_id, window_id):
    cmd = 'Windows.window{0}.CanYCentre'.format( window_id )
    result = client.corio_send_command(screen_id, cmd)
    value = tools.getTVOneParameter( result )
    return int(value)

def set_window_position_batched(screen_id, window_id, x, y):
    cmds = []
    cmds.append( 'Windows.window{0}.CanXCentre = {1}'.format( window_id, x) )
    cmds.append( 'Windows.window{0}.CanYCentre = {1}'.format( window_id, y) )
    client.corio_send_batchcommands(screen_id, cmds)

def set_window_geometry_batched(screen_id, window_id, x, y, w, h):
    cmds = []
    cmds.append( 'Windows.window{0}.CanXCentre = {1}'.format( window_id, x) )
    cmds.append( 'Windows.window{0}.CanYCentre = {1}'.format( window_id, y) )
    cmds.append( 'Windows.window{0}.CanWidth = {1}'.format( window_id, w) )
    cmds.append( 'Windows.window{0}.CanHeight = {1}'.format( window_id, h) )
    client.corio_send_batchcommands(screen_id, cmds)

def set_window_zorder(screen_id, window_id, z):
    cmd = 'Windows.window{0}.Zorder = {1}'.format( window_id, z)
    client.corio_send_command(screen_id, cmd)

def get_window_zorder(screen_id, window_id):
    cmd = 'Windows.window{0}.Zorder'.format( window_id )
    result = client.corio_send_command(screen_id, cmd)
    value = tools.getTVOneParameter( result )
    return int(value)

def set_window_rotation(screen_id, window_id, angle):
    cmd = 'Windows.window{0}.RotateDeg = {1}'.format( window_id, angle)
    client.corio_send_command(screen_id, cmd)

def get_window_rotation(screen_id, window_id):
    cmd = 'Windows.window{0}.RotateDeg'.format( window_id )
    result = client.corio_send_command(screen_id, cmd)
    value = tools.getTVOneParameter( result )
    return int(value)

def set_window_border_pix_width(screen_id, window_id, w):
    cmd = 'Windows.window{0}.BdrPixWidth = {1}'.format( window_id, w)
    client.corio_send_command(screen_id, cmd)

def set_window_border_color(screen_id, window_id, color):
    cmd = 'Windows.window{0}.BdrRGB = {1}'.format( window_id, color)
    client.corio_send_command(screen_id, cmd)

def set_window_hflip(screen_id, window_id, flag):
    switch = "Off"
    if( flag ):
        switch = "On"
    cmd = 'Windows.window{0}.HFlip = {1}'.format( window_id, switch)
    client.corio_send_command(screen_id, cmd)

def set_window_vflip(screen_id, window_id, flag):
    switch = "Off"
    if( flag ):
        switch = "On"
    cmd = 'Windows.window{0}.VFlip = {1}'.format( window_id, switch)
    client.corio_send_command(screen_id, cmd)

def set_window_transition_fade(screen_id, window_id, flag):
    switch = "Off"
    if( flag ):
        switch = "On"
    cmd = 'Windows.window{0}.SCFTB = {1}'.format( window_id, switch)
    client.corio_send_command(screen_id, cmd)

def set_window_transition_hshrink(screen_id, window_id, flag):
    switch = "Off"
    if( flag ):
        switch = "On"
    cmd = 'Windows.window{0}.SCHShrink = {1}'.format( window_id, switch)
    client.corio_send_command(screen_id, cmd)

def set_window_transition_vshrink(screen_id, window_id, flag):
    switch = "0"
    if( flag ):
        switch = flag	# from -7 to 7
    cmd = 'Windows.window{0}.SCVShrink = {1}'.format( window_id, switch)
    client.corio_send_command(screen_id, cmd)

def set_window_transition_spin(screen_id, window_id, flag):
    switch = "Off"
    if( flag ):
        switch = "On"
    cmd = 'Windows.window{0}.SCSpin = {1}'.format( window_id, switch)
    client.corio_send_command(screen_id, cmd)

def get_window_source(screen_id, window_id):
    cmd = 'Windows.window{0}.Input'.format( window_id)
    result = client.corio_send_command(screen_id, cmd)	# receive something as "Window1.Input = Slot3.In1 \n !Done Window1.Input"
    value = tools.getTVOneParameter( result )
    return value

def set_window_source(screen_id, window_id, source_name):
    cmd = 'Windows.window{0}.Input = {1}'.format( window_id, source_name)
    client.corio_send_command(screen_id, cmd)

def get_window_input(screen_id, window_id):
    value = get_window_source(screen_id, window_id)
    tab = re.findall(r'\d+', value)
    #print "tuple=", tab[0], ",", tab[1]
    return (tab[0], tab[1])

def set_window_input(screen_id, window_id, slot_id, input_id):
    cmd = 'Windows.window{0}.Input = Slot{1}.In{2}'.format( window_id, slot_id, input_id)
    client.corio_send_command(screen_id, cmd)

def get_window_touch_ip(screen_id, window_id):
    ip = ""
    slot_id, input_id = get_window_input(screen_id, window_id)
    source_str = 'Slot{0}.In{1}'.format(slot_id, input_id)
    input = [input for input in config['inputs'] if input['slot'] == source_str]

    return ip

#
# API
#

def set_window_size(screen_id, window_id, w, h):
    set_window_width(screen_id, window_id, w)
    set_window_height(screen_id, window_id, h)

def get_window_size(screen_id, window_id):
    w = get_window_width(screen_id, window_id)
    h = get_window_height(screen_id, window_id)
    return {"w": w, "h": h}

def set_window_position(screen_id, window_id, x, y):
    set_window_x_position(screen_id, window_id, x)
    set_window_y_position(screen_id, window_id, y)

def get_window_position(screen_id, window_id):
    x = get_window_x_position(screen_id, window_id)
    y = get_window_y_position(screen_id, window_id)
    return {"x": x, "y": y}

def set_window_geometry(screen_id, window_id, x, y, w, h):
    #set_window_width(screen_id, window_id, w)
    #set_window_height(screen_id, window_id, h)
    #set_window_x_position(screen_id, window_id, x)
    #set_window_y_position(screen_id, window_id, y)
    set_window_geometry_batched(screen_id, window_id, x, y, w, h)

def get_window_geometry(screen_id, window_id):
    x = get_window_x_position(screen_id, window_id)
    y = get_window_y_position(screen_id, window_id)
    w = get_window_width(screen_id, window_id)
    h = get_window_height(screen_id, window_id)
    return {"x": x, "y": y, "w": w, "h": h}

def set_window_angle(screen_id, window_id, a):
    set_window_rotation(screen_id, window_id, a)

def get_window_angle(screen_id, window_id):
    a = get_window_rotation(screen_id, window_id);
    return {"angle": a}

def move_window(screen_id, window_id, delta_x, delta_y):
    x = get_window_x_position(screen_id, window_id)
    y = get_window_y_position(screen_id, window_id)
    set_window_position_batched(screen_id, window_id, x+delta_x, y+delta_y)

def rotate_window(screen_id, window_id, delta_a):
    a = get_window_rotation(screen_id, window_id);
    set_window_rotation(screen_id, window_id, a+delta_a)

def set_window_border(screen_id, window_id, w, color):
    set_window_border_pix_width(screen_id, window_id, w)
    set_window_border_color(screen_id, window_id, color)

def set_window_effect(screen_id, window_id, effects_array):
    for effect in effects_array:
        if effect == "fade":
            set_window_transition_fade(screen_id, window_id, True)
        elif effect == "hshrink":
            set_window_transition_hshrink(screen_id, window_id, True)
        elif effect == "vshrink":
            set_window_transition_vshrink(screen_id, window_id, True)
        elif effect == "spin":
            set_window_transition_spin(screen_id, window_id, 1)

def set_window_quality(screen_id, window_id, q):
    slot_id, input_id = get_window_input(screen_id, window_id)
    if q == "low":
        contents.set_content_resolution(screen_id, slot_id, input_id, "640x480p60")
    elif q == "medium":
        contents.set_content_resolution(screen_id, slot_id, input_id, "1280x720p60")
    elif q == "high":
        contents.set_content_resolution(screen_id, slot_id, input_id, "1920x1080p60")

def get_window_quality(screen_id, window_id):
    slot_id, input_id = get_window_input(screen_id, window_id)
    resolutionObj = contents.get_content_resolution(screen_id, slot_id, input_id)
    return resolutionObj

def get_rich_window( win, win_id, screen_id ):
    obj = {}
    obj['id'] = win_id;
    obj['x']  = win['CanXCentre']
    obj['y']  = win['CanYCentre']
    obj['w']  = win['CanWidth']
    obj['h']  = win['CanHeight']
    obj['z']  = win['Zorder']
    obj['alias'] 	= win['Alias']
    obj['fullname'] = win['FullName']
    obj['input'] 	= win['Input']
    obj['inputalias'] = slots.get_input_alias( screen_id, win['Input'] )
    return obj

def get_rich_window_list(screen_id):
    # First, get window list
    windows = []
    cmd = 'Windows'
    result = client.corio_send_command(screen_id, cmd)  # result "Windows.Window1 = <...>\r\nWindows.Window2 = <...>\r\nWindows.Window3 = <...>\r\nWindows.Window4 = <...>\r\n"
    windows = tools.convertTVONEListToJsonList(result, True, True)

    # then retrieve all windows infos
    for key in windows.keys():
        win = get_window(screen_id, key)
        #print "win=" + repr(win)
        obj = get_rich_window(win, key, screen_id)

        windows[key] = obj

    #print "win=" + repr(windows)
    return windows

def refresh_window_canvas(screen_id):
    cmds = []
    cmds.append( 'Windows' )
    for win_id in range(1, 37):
        cmds.append( 'Windows.window{0}.Canvas'.format( win_id ) )
    client.corio_send_batchcommands(screen_id, cmds)
