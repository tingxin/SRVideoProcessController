
# canvas.py	:	Canvas management module

import client
import tools
import windows
import slots

import re

def get_canvases_list(screen_id):
    canvases = {}
    cmd = 'Canvases'
    result = client.corio_send_command(screen_id, cmd)
    list = tools.convertTVONEListToJsonList(result, True, True)
    return list

def get_canvas(screen_id, canvas_id):
    cmd = 'Canvas{0}'.format( canvas_id )
    result = client.corio_send_command(screen_id, cmd)
    list = tools.convertTVONEListToJsonList(result)
    return list

def get_windows_on_canvas(screen_id, canvas_id):
    windows = []
    # print "get_windows_on_canvas(): --> <--"
    canvas = get_canvas( screen_id, canvas_id )
    #extract windows list
    value = canvas['WindowList']
    tokens = value.split(',')
    for token in tokens:
        tab = re.findall(r'\d+', token)
        if( len(tab) > 0 ):
            windows.append( int(tab[0]) )

    return windows

def get_rich_windows_on_canvas(screen_id, canvas_id):
    windowsArray = []
    # print "get_windows_on_canvas(): --> <--"
    canvas = get_canvas( screen_id, canvas_id )
    #extract windows list
    value = canvas['WindowList']
    tokens = value.split(',')
    for token in tokens:
        tab = re.findall(r'\d+', token)
        if( len(tab) > 0 ):
            win_id = int(tab[0])
            win = windows.get_window(screen_id, win_id)
            #print "win="+repr(win)
            obj = windows.get_rich_window(win, win_id, screen_id)
            windowsArray.append(obj)

    return windowsArray
