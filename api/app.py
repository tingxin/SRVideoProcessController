from flask import Flask, abort, make_response, jsonify, request, current_app, g
from flask import send_file
import json
from datetime import timedelta
from datetime import datetime
from functools import update_wrapper
import requests
import urllib
from pprint import pprint
import simplejson

from tvonecorio import client
from tvonecorio import configs
from tvonecorio import slots
from tvonecorio import windows
from tvonecorio import presets
from tvonecorio import contents
from tvonecorio import canvas
from tvonecorio import configuration
from tvonecorio import scenarios
from tvonecorio import sound
from tvonecorio import database

app = Flask(__name__)

supported_effects = ['fade', 'hschrink', 'vschrink', 'spin']

RESULT_OK 	 = { 'result' : 'OK', 'content' : '' }
RESULT_ERROR = { 'result' : 'ERROR', 'content' : '' }
def make_OK_response_with_content( content ) :
    response = RESULT_OK;
    response['content'] = content
    return make_response(jsonify(response), 200)
def make_ERROR_response_with_content( content ) :
    response = RESULT_ERROR;
    response['content'] = content
    return make_response(jsonify(response), 200)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        #print "headers=" + repr(options_resp.headers)
        if not 'allow' in options_resp.headers:
            return u'HEAD, OPTIONS, GET'
        else:
            return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Last-Modified'] = datetime.now()
            h['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            h['Pragma'] = 'no-cache'
            h['Expires'] = '-1'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
                print repr(resp)
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


@app.route("/")
@crossdomain(origin='*')
def hello():
	return 'Hello World!'


#
# Screen informations management
#


@app.route('/pirl/v1/displays', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_screens():
	screens = client.corio_get_screens()
	return make_OK_response_with_content( screens )


@app.route('/pirl/v1/displays/<int:screen_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_screen(screen_id):
	screen = client.corio_get_screen( screen_id )
	if len(screen) == 0:
		return make_ERROR_response_with_content( "Can't find screen with id '"+repr(screen_id)+"'" )
	return make_OK_response_with_content( screen[0] )


#
# Configs management
#


@app.route('/pirl/v1/displays/<int:screen_id>/configs', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_configs(screen_id):
	confs = []
	try:
		confs = configs.get_configs_list( screen_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( confs )


@app.route('/pirl/v1/displays/<int:screen_id>/configs/current', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_current_config(screen_id):
	name = ""
	try:
		name = configs.get_current_config_name( screen_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( name )


@app.route('/pirl/v1/displays/<int:screen_id>/configs/<int:config_id>', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_config(screen_id, config_id):
	config = {}
	try:
		config = configs.get_config( screen_id, config_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( config )


# Backup the specified configuration from NAND to SD card. This is similar to "System.BackupToSDCard()" but for this configuration only.
@app.route('/pirl/v1/displays/<int:screen_id>/configs/<int:config_id>/save', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def save_config(screen_id, config_id):
	try:
		configs.save_config( screen_id, config_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'config': config_id} )


# Restore the specified configuration from SD card to NAND. This is similar to "System.RestoreBackup()" but for this configuration only.
@app.route('/pirl/v1/displays/<int:screen_id>/configs/<int:config_id>/load', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def load_config(screen_id, config_id):
	try:
		configs.load_config( screen_id, config_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'config': config_id} )


# Remove the specified configuration from the SD card
@app.route('/pirl/v1/displays/<int:screen_id>/configs/<int:config_id>/delete', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def delete_config(screen_id, config_id):
	try:
		configs.delete_config( screen_id, config_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'config': config_id} )



#
# Slots management
#



@app.route('/pirl/v1/displays/<int:screen_id>/slots/', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_slots(screen_id):
    _slots = []
    try:
        _slots = slots.get_slots_list(screen_id)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( _slots )


@app.route('/pirl/v1/displays/<int:screen_id>/slots/inputs', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_input_slots(screen_id):
    _slots = []
    try:
        _slots = slots.get_inputs_slots_list(screen_id)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( _slots )



@app.route('/pirl/v1/displays/<int:screen_id>/slots/<int:slot_id>', methods = ['GET', 'OPTIONS'])
def get_slot(screen_id, slot_id):
    result = {}
    try:
        result = slots.get_slot(screen_id, slot_id)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( result )


@app.route('/pirl/v1/displays/<int:screen_id>/slots/<int:slot_id>/in/<int:index>', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_slot_in(screen_id, slot_id, index):
    result = {}
    try:
        result = slots.get_slot_in(screen_id, slot_id, index)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( result )


@app.route('/pirl/v1/displays/<int:screen_id>/slots/<int:slot_id>/out/<int:index>', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_slot_out(screen_id, slot_id, index):
	result = {}
	try:
		result = slots.get_slot_out(screen_id, slot_id, index)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( result )

from functools import wraps, update_wrapper
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        max_age=21600
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Methods'] = "HEAD, GET"
        response.headers['Access-Control-Max-Age'] = str(max_age)

        print repr(response)
        return response

    return update_wrapper(no_cache, view)

@app.route('/pirl/v1/displays/<int:screen_id>/slots/<int:slot_id>/in/<int:index>/image', methods = ['GET', 'OPTIONS'])
@nocache
def get_slot_in_image(screen_id, slot_id, index):
    result = {}
    try:
        filename = slots.get_slot_in_image(screen_id, slot_id, index)
        return send_file(filename, mimetype='image/png')
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( result )



#
# windows management
#



@app.route('/pirl/v1/displays/<int:screen_id>/panels', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_windows(screen_id):
	wins = []
	try:
		wins = windows.get_windows_list(screen_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( wins )

@app.route('/pirl/v1/displays/<int:screen_id>/panels/rich', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_rich_windows_list(screen_id):
	wins = []
	try:
		wins = windows.get_rich_window_list(screen_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( wins )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window(screen_id, window_id):
	window = {}
	try:
		window = windows.get_window(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( window )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/source', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window_source(screen_id, window_id):
	source = {}
	try:
		source = windows.get_window_source(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( source )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/source/<int:slot_id>/<int:input_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_source(screen_id, window_id, slot_id, input_id):
	source = {}
	try:
		source = windows.set_window_input(screen_id, window_id, slot_id, input_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( source )
@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/source/<source_name>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_source_byname(screen_id, window_id, source_name):
	source = {}
	try:
		source = windows.set_window_source(screen_id, window_id, source_name)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( source )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/size', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window_size(screen_id, window_id):
	size = {}
	try:
		size = windows.get_window_size(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( size )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/size=<int:w>,<int:h>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_size(screen_id, window_id, w, h):
	try:
		windows.set_window_size(screen_id, window_id, w, h)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'window': window_id, 'w': w, 'h': h} )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/position', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window_position(screen_id, window_id):
	size = {}
	try:
		size = windows.get_window_position(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( size )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/position=<x_str>,<y_str>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_position(screen_id, window_id, x_str, y_str):
	x = int( x_str )
	y = int( y_str )
	try:
		windows.set_window_position(screen_id, window_id, x, y)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'window': window_id, 'x': x, 'y': y} )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/geometry', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window_geometry(screen_id, window_id):
	size = {}
	try:
		size = windows.get_window_geometry(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( size )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/geometry=<x_str>,<y_str>,<int:w>,<int:h>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_geometry(screen_id, window_id, x_str, y_str, w, h):
	x = int( x_str )
	y = int( y_str )
	try:
		windows.set_window_geometry(screen_id, window_id, x, y, w, h)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'window': window_id, 'x': x, 'y': y, 'w': w, 'h': h} )

@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/zorder', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window_zorder(screen_id, window_id):
	zorder = {}
	try:
		zorder = windows.get_window_zorder(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( zorder )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/zorder=<int:z>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_zorder(screen_id, window_id, z):
	try:
		windows.set_window_zorder(screen_id, window_id, z)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'window': window_id, 'z': z} )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/move=<x_str>,<y_str>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_move(screen_id, window_id, x_str, y_str):
	x = int( x_str )
	y = int( y_str )
	try:
		windows.move_window(screen_id, window_id, x, y)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'window': window_id, 'deltax': x, 'deltay': y} )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/angle', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window_angle(screen_id, window_id):
	angle = {}
	try:
		angle = windows.get_window_angle(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( angle )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/angle=<str>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_angle(screen_id, window_id, str):
	angle = int( str )
	try:
		angle = windows.set_window_angle(screen_id, window_id, angle)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'panel': window_id, 'angle': angle} )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/rotate=<str>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_rotate(screen_id, window_id, str):
	angle = int( str )
	try:
		windows.rotate_window(screen_id, window_id, angle)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'panel': window_id, 'delta_angle': angle} )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/border=<colorstr>,<int:size>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_border(screen_id, window_id, colorstr, size):
	if colorstr.startswith('#'):
		colorhexa = colorstr[1:]
		if len(colorhexa) == 3:
			str = colorhexa[0]+colorhexa[0]+colorhexa[1]+colorhexa[1]+colorhexa[2]+colorhexa[2]
			color = int(str, 16)
			#print "1, #" + str + "=" + repr(color)
			try:
				windows.set_window_border(screen_id, window_id, size, color)
			except Exception, e:
				return make_ERROR_response_with_content( repr(e) )
		elif len(colorhexa) == 6:
			color = int(colorhexa, 16)
			#print "2, #" + colorhexa + "=" + repr(color)
			try:
				windows.set_window_border(screen_id, window_id, size, color)
			except Exception, e:
				return make_ERROR_response_with_content( repr(e) )
		else:
			return make_ERROR_response_with_content( "Bad color format. Use '#rrggbb' or '#rgb' format" )
	else:
		return make_ERROR_response_with_content( "Bad color format. Use '#rrggbb' or '#rgb' format" )
	return make_OK_response_with_content( {'display': screen_id, 'panel': window_id, 'color': colorstr, 'size': size} )


@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/quality', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_window_quality(screen_id, window_id):
	res = ''
	try:
		res = windows.get_window_quality(screen_id, window_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( res )


# quality is high/medium/low
@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/quality=<q>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_window_quality(screen_id, window_id, q):
	if q!='low' and q!='medium' and q!='high':
		return make_ERROR_response_with_content( "Bad quality format. Use 'low', 'medium' or 'high' key words" )
	try:
		windows.set_window_quality(screen_id, window_id, q)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'panel': window_id, 'quality': q} )


# effect is [fade,hschrink,vschrink,spin]
@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:window_id>/effect=<e>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def api_set_display_effect(screen_id, window_id, e):
	effects_array = e.split("+")

	# check parameter validity
	if len(effects_array) == 0:
		return make_ERROR_response_with_content( "Invalid effects. Effect must be separated by '+'. Ex: 'fade+hschrink+spin'" )
	for effect in effects_array:
		if effect not in supported_effects:
			return make_ERROR_response_with_content( "Unsupported effect. Supported effects are: "+repr(supported_effects)+". Effect must be separated by '+'. Ex: 'fade+hschrink+spin'" )

	try:
		windows.set_window_effect(screen_id, window_id, effects_array)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'panel': window_id, 'effect': repr(effects_array)} )



#
# Presets management
#



@app.route('/pirl/v1/displays/<int:screen_id>/presets', methods=['GET'])
@crossdomain(origin='*')
def get_presets(screen_id):
	presetsList = {}
	try:
		presetsList = presets.get_presets_list(screen_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( presetsList )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/current', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_active_preset(screen_id):
	active_preset_id = -1;
	try:
		active_preset_id = presets.get_active_preset(screen_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( active_preset_id )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/<int:preset_id>/load', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def load_preset(screen_id, preset_id):
	try:
		presets.set_active_preset( screen_id, preset_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( preset_id )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/save', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def save_active_preset(screen_id):
	try:
		presets.save_active_preset(screen_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id, 'status': 'saved'} )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/get', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_editable_preset(screen_id):
	get_preset_id = -1;
	try:
		get_preset_id = presets.get_editable_preset( screen_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( get_preset_id )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/<int:preset_id>/set', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def set_editable_preset(screen_id, preset_id):
	try:
		presets.set_editable_preset( screen_id, preset_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( preset_id )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/<int:preset_id>/loadAndEdit', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def load_and_edit_preset(screen_id, preset_id):
	try:
		presets.set_active_preset( screen_id, preset_id )
		presets.set_editable_preset( screen_id, preset_id )
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( preset_id )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/rename/<name>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def rename_active_preset(screen_id, name):
	try:
		presets.rename_active_preset(screen_id, name)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id} )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/delete', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def delete_active_preset(screen_id):
	try:
		presets.delete_active_preset(screen_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( {'display': screen_id} )

@app.route('/pirl/v1/displays/<int:screen_id>/presets/new/<int:preset_id>/<name>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def create_preset(screen_id, preset_id, name):
    try:
        presets.create_preset(screen_id, preset_id, name)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( preset_id )



#
# Canvas management
#



@app.route('/pirl/v1/displays/<int:screen_id>/canvas', methods=['GET'])
@crossdomain(origin='*')
def get_canvases(screen_id):
	canvases = {}
	try:
		canvases = canvas.get_canvases_list(screen_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( canvases )


@app.route('/pirl/v1/displays/<int:screen_id>/canvas/<int:canvas_id>', methods=['GET'])
@crossdomain(origin='*')
def get_canvas(screen_id, canvas_id):
	list = {}
	try:
		list = canvas.get_canvas(screen_id, canvas_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( list )


@app.route('/pirl/v1/displays/<int:screen_id>/canvas/<int:canvas_id>/panels', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_windows_in_canvas(screen_id, canvas_id):
	list = {}
	try:
		list = canvas.get_windows_on_canvas(screen_id, canvas_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( list )


@app.route('/pirl/v1/displays/<int:screen_id>/canvas/<int:canvas_id>/panels/rich', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_rich_windows_in_canvas(screen_id, canvas_id):
	list = {}
	try:
		list = canvas.get_rich_windows_on_canvas(screen_id, canvas_id)
	except Exception, e:
		return make_ERROR_response_with_content( repr(e) )
	return make_OK_response_with_content( list )


#
# Scenarios management
#


@app.route('/pirl/v1/scenarios', methods=['GET'])
@crossdomain(origin='*')
def get_scenarios():
    scenarios_list = {}
    try:
        scenarios_list = scenarios.get_scenarios_list()
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( scenarios_list )

@app.route('/pirl/v1/scenarios/create/<name>/<left_presetstr>/<right_presetstr>/<audio_src>/<int:audio_lvl>/<int:duration>', methods=['GET'])
@crossdomain(origin='*')
def create_scenario(name, left_presetstr, right_presetstr, audio_src, audio_lvl, duration):
    try:
        left_preset  = int(left_presetstr)
        right_preset = int(right_presetstr)
        scenarios.create_scenario(name, left_preset, right_preset, audio_src, audio_lvl, duration)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_response("", 200)

@app.route('/pirl/v1/scenarios/delete/<int:id>', methods=['GET'])
@crossdomain(origin='*')
def delete_scenario(id):
    try:
        scenarios.delete_scenario(id)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_response("", 200)

@app.route('/pirl/v1/scenarios/update/<int:id>/<name>/<left_presetstr>/<right_presetstr>/<audio_src>/<int:audio_lvl>/<int:duration>', methods=['GET'])
@crossdomain(origin='*')
def update_scenario(id, name, left_presetstr, right_presetstr, audio_src, audio_lvl, duration):
    scenarios_list = {}
    try:
        left_preset  = int(left_presetstr)
        right_preset = int(right_presetstr)
        scenarios.update_scenario(id, name, left_preset, right_preset, audio_src, audio_lvl, duration)
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_response("", 200)


#
# Connections management
#


@app.route('/pirl/v1/connections', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_connections():
	conns = client.corio_get_connections()
	return make_OK_response_with_content( conns )


@app.route('/pirl/v1/connections/release', methods = ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def release_connections():
	conns = client.corio_release_connections()
	return make_OK_response_with_content( conns )


#
# DISPLAYS
#

@app.route('/pirl/v1/displays/<int:screen_id>/size=<int:x>,<int:y>,<int:w>,<int:h>', methods=['GET'])
@crossdomain(origin='*')
def api_set_screen_size(screen_id, x, y, w, h):
	#c = corio_get(screen[0])
	#c.windows_set_size(screen_id, x, y, w, h)

	return make_response(jsonify({'display': screen_id, 'x': x, 'y': y, 'w': w, 'h': h}), 200)
	#return jsonify({'ret': 'ok'})

#
# PANELS
#

@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/shape=<f>', methods=['GET'])
@crossdomain(origin='*')
def api_set_display_shape(screen_id, panel_id, f):
	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'shape': f}), 200)

#@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/border=<color>,<int:size>', methods=['GET'])
#def api_set_display_border(screen_id, panel_id, color, size):
#	screen = get_screen_from_screen_id( screen_id )
#	c = corio_get( screen )
#	if type(color) is not int:
#		abort(400)
#	c.set_window_border(panel_id, size, color)
#	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'color': color, 'size': size}), 200)

# scale is fit/clip/center/mosaic/...
@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/scale=<scale>', methods=['GET'])
@crossdomain(origin='*')
def api_set_display_scale(screen_id, panel_id, scale):
	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'scale': scale}), 200)

# quality is high/medium/low
#@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/quality=<q>', methods=['GET'])
#def api_set_display_quality(screen_id, panel_id, q):
#	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'quality': q}), 200)

# effect is [fade,hschrink,vschrink,spin]
#@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/effect=<e>', methods=['GET'])
#def api_set_display_effect(screen_id, panel_id, e):
#	effects_array = e.split("+")
#	screen = get_screen_from_screen_id( screen_id )
#	c = corio_get( screen )
#	#c.set_window_border(panel_id, effects_array)
#	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'effect': repr(tab)}), 200)

#
# CONTENTS
#

@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/content/url=<url>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def api_set_display_url(screen_id, panel_id, url):
	#screen = get_screen_from_screen_id( screen_id )
	#c = corio_get( screen )
	#c.play_content(screen_id, panel_id, url)
	print "ok"
	input = "127.0.0.1:8080"
	uri = "http://" + input + "/requests/status.xml?command=in_play&input=" + url
	#uri = "http://" + input + "/requests/status.xml?command=in_play&input=" + urllib.quote('E:\\medias\\1alaska.mpeg', safe='')

	try:
		print repr(uri)
		r = requests.get(uri)
	except requests.exceptions.Timeout as e:
		# Maybe set up for a retry, or continue in a retry loop
		return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'err': "requests.exceptions.Timeout", "err": e}), 200)
	except requests.exceptions.TooManyRedirects as e:
		# Tell the user their URL was bad and try a different one
		return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'err': "requests.exceptions.TooManyRedirects", "err": e}), 200)
	except requests.exceptions.RequestException as e:
		# catastrophic error. bail.
		print e
		return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'err': "requests.exceptions.RequestException", "err": e}), 200)
	except e:
		print e
		return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'err': "General Exception", "err": e}), 200)
	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'url': url}), 200)

@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/content/input=<in_id>', methods=['GET'])
@crossdomain(origin='*')
def api_set_display_input(screen_id, panel_id, in_id):
	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'input': in_id}), 200)


#
# Sound
#


@app.route('/pirl/v1/sound/up', methods=['GET'])
@crossdomain(origin='*')
def api_sound_up():
    sound.sound_up()
    return make_response("", 200)

@app.route('/pirl/v1/sound/down', methods=['GET'])
@crossdomain(origin='*')
def api_sound_down():
    sound.sound_down()
    return make_response("", 200)

@app.route('/pirl/v1/sound/mute', methods=['GET'])
@crossdomain(origin='*')
def api_sound_mute():
    sound.sound_mute()
    print "iiuyiuyiuy"
    return make_OK_response_with_content("")

@app.route('/pirl/v1/sound/unmute', methods=['GET'])
@crossdomain(origin='*')
def api_sound_unmute():
    sound.sound_unmute()
    return make_OK_response_with_content("")

@app.route('/pirl/v1/sound/mute/get', methods=['GET'])
@crossdomain(origin='*')
def api_sound_get_muted( ):
    result = sound.sound_get_muted( )
    return make_OK_response_with_content(result)

@app.route('/pirl/v1/sound/input/get', methods=['GET'])
@crossdomain(origin='*')
def api_sound_get_input():
    result = sound.sound_get_input()
    return make_OK_response_with_content(result)

@app.route('/pirl/v1/sound/input/set/<input_str>', methods=['GET'])
@crossdomain(origin='*')
def api_sound_set_input( input_str ):
    sound.sound_set_input( input_str )
    return make_response("", 200)

@app.route('/pirl/v1/sound/settings', methods=['GET'])
@crossdomain(origin='*')
def api_sound_get_settings():
    result = sound.api_sound_get_settings()
    return make_OK_response_with_content(result)



#
# Various
#


@app.route('/pirl/v1/source/<screen_name>/<src_str>/touchctrl/<ip_str>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def api_set_source_touch_ctrl(screen_name, src_str, ip_str):
    screen = client.corio_get_screen_by_name( screen_name )
    if len(screen) == 0:
        return make_ERROR_response_with_content( "Can't find screen with name '"+repr(screen_name)+"'" )

    screen_id = repr(screen[0]['id'])
    inputs = database.get_input_by_slot( src_str, screen_id)
    if len(inputs) == 0:
        database.create_input(src_str, "", screen_id, ip_str, "", "")
    else:
        database.update_input_touch_ctrl(src_str, screen_id, ip_str)

    return make_response(jsonify({'wall': screen_id, 'source': src_str, 'touch_ip': ip_str}), 200)


@app.route('/pirl/v1/source/<screen_name>/<src_str>/videoctrl/<ip_str>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def api_set_source_video_ctrl(screen_name, src_str, ip_str):
    screen = client.corio_get_screen_by_name( screen_name )
    if len(screen) == 0:
        return make_ERROR_response_with_content( "Can't find screen with name '"+repr(screen_name)+"'" )

    screen_id = repr(screen[0]['id'])
    inputs = database.get_input_by_slot( src_str, screen_id)
    if len(inputs) == 0:
        database.create_input(src_str, "", screen_id, "", "", ip_str)
    else:
        database.update_input_video_ctrl(src_str, screen_id, ip_str)

    return make_response(jsonify({'wall': screen_id, 'source': src_str, 'video_ip': ip_str}), 200)


@app.route('/pirl/v1/source/<screen_name>/<src_str>/name/<name_str>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def api_set_source_name(screen_name, src_str, name_str):
    screen = client.corio_get_screen_by_name( screen_name )
    if len(screen) == 0:
        return make_ERROR_response_with_content( "Can't find screen with name '"+repr(screen_name)+"'" )

    screen_id = repr(screen[0]['id'])
    inputs = database.get_input_by_slot( src_str, screen_id)
    if len(inputs) == 0:
        database.create_input(src_str, name_str, screen_id, "", "", "")
    else:
        database.update_input_name(src_str, screen_id, name_str)

    return make_response(jsonify({'wall': screen_id, 'source': src_str, 'name': name_str}), 200)


@app.route('/pirl/v1/source/<screen_name>/<src_str>/pict', methods=['POST', 'PUT', 'OPTIONS'])
@crossdomain(origin='*')
def api_set_source_picture(screen_name, src_str):
    screen = client.corio_get_screen_by_name( screen_name )
    if len(screen) == 0:
        return make_ERROR_response_with_content( "Can't find screen with name '"+repr(screen_name)+"'" )

    screen_id = repr(screen[0]['id'])
    filename = ''
    inputs = database.get_input_by_slot( src_str, screen_id)
    try:
        if len(inputs) == 0:
            filename = "./thumbnail/" + screen_id + "_" + src_str + ".png"
            database.create_input(src_str, "", screen_id, "", filename, "")
        else:
            filename = "./thumbnail/" + str(inputs[0]['wall_id']) + "_" + str(inputs[0]['slot']) + ".png"
            database.update_input_pict_name(src_str, screen_id, filename)
        f = request.files['files']
        f.save( filename )
    except:
        print "api_set_source_picture(): error when receive thumbnail for " + src_str

    return make_response(jsonify({'wall': screen_id, 'source': src_str, 'filename': filename}), 200)

@app.route('/pirl/v1/source', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def api_get_all_inputs_alias():
    sources_list = {}
    try:
        sources_list = database.get_inputs_alias_list()
    except Exception, e:
        return make_ERROR_response_with_content( repr(e) )
    return make_OK_response_with_content( sources_list )



@app.teardown_appcontext
def close_connection(exception):
    database.close_database()

#
#yyy8
#

@app.route('/pirl/v1/displays/<int:screen_id>/panels/<int:panel_id>/content/crop=<int:l>,<int:t>,<int:r>,<int:b>', methods=['GET'])
def api_set_display_crop(screen_id, panel_id, l, t, r, b):
	screen = get_screen_from_screen_id( screen_id )
	c = corio_get( screen )
	c.set_crop(panel_id, l, t, r, b)
	return make_response(jsonify({'display': screen_id, 'panel': panel_id, 'left': l, 'top': t, 'right': r, 'bottom': b}), 200)

#@app.errorhandler(404)
#@crossdomain(origin='*')
#def not_found(error):
#    return make_response(jsonify({'error': 404}), 200)

@app.errorhandler(400)
@crossdomain(origin='*')
def not_found(error):
	return make_response(jsonify({'error': 400}), 200)

@app.errorhandler(500)
@crossdomain(origin='*')
def not_found(error):
	return make_response(jsonify({'error': 500}), 200)

if __name__ == "__main__":

	#configuration.init_config()

	# start flask
	app.run(debug=True, host='localhost', port=5001)
