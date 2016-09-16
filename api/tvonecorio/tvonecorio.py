import telnetlib
import logging
import time
import re

DEFAULT_PORT = 10001
DEFAULT_USER = 'admin'
DEFAULT_PASSWORD = 'adminpw'
DEFAULT_TIMEOUT = 5

DEFAULT_EXPECT = '!Done '

logging.basicConfig(level=logging.INFO)

class Client:
	def __init__(self, hostname, port=DEFAULT_PORT,
								 user=DEFAULT_USER,
								 password=DEFAULT_PASSWORD):
		self.hostname = hostname
		self.port = port
		self.user = user
		self.password = password
		self.connection = None
		self.logged = False

	def connected(self):
		return self.connection is not None

	def logged(self):
		return self.logged

	def login(self):
		try:
			self.connection = telnetlib.Telnet(self.hostname, self.port, DEFAULT_TIMEOUT)
		except:
			raise Exception("Can't connect to: {0}:{1}".format(self.hostname, self.port))

		self.connection.set_debuglevel(10)

		self.connection.read_until("""Please login. Use 'login(username,password)'\r\n""")

		self.connection.write('login({0},{1})\n'.format(self.user, self.password))

		expected = """!Info : User {0} Logged In\r\n""".format(self.user)
		result = self.connection.read_until(expected)
		if result != expected:
			raise Exception("Invalid login: {0}".format(result))
		else:
			self.logged = True
			
	def close(self):
		if self.logged:
			self.connection.write('logout\n')
		self.connection.close()
		self.logged = False
		

	def send_command(self, command, expected=None):
		response = ""
		if not self.logged:
			self.login()
		result = self.connection.write(command + '\n')
		#print "connection write=" + repr(result)
		
		if expected is not None:
			# the end is "!Done <cmd>\r\n" or "!Error ... <cmd>\r\n"
			expected = "!Done " + command + "\r\n"
			try:
				index, obj, response = self.connection.expect( [re.compile(expected)] )
				#print "connection index="+repr(index) + ", obj="+repr(obj) + ", response=" + repr(response)
			except EOFError, e:
				print "Exception: e="+repr(e)

		return response
		
#
#  Tools
#

	# convertTVONEListToJson(): convert a TVOne list as "Configs.Config1 = <...>\r\nConfigs.Config2 = <...>\r\nConfigs.Config3...\r\n" to 
	# json object as 
	def convertTVONEListToJsonList(self, tvone_list, remove_prefix=True, extract_id=False):
		list = {}	# type dictionaries
		paramlist = tvone_list.split('\r\n')
		for param in paramlist:
			values = param.split('=')
			if len( values ) > 1 :
				values[0] = values[0].strip()
				values[1] = values[1].strip()
				#if values[1][-1] == '\r':
				#	values[1] = values[1][0:-1]
				if remove_prefix :
					start_pos = values[0].rfind(".") + 1
					values[0] = values[0][start_pos:]
				if extract_id :
					tokens = re.findall(r'\d+', values[0])
					if len(tokens) > 0 :
						values[0] = tokens[0]
				list[ values[0] ] = values[1]
		return list
		
	def convertTVONEListToJsonArray(self, tvone_list, remove_prefix=True, extract_id=False):
		array = []
		paramlist = tvone_list.split('\n')
		for param in paramlist:
			values = param.split('=')
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
	
	def getTVONEValue(self, parameter):
		value = ""
		tokens = parameter.split('=')
		if( len(tokens) > 0 ):
			value = tokens[1].strip()
			tokens = value.split('\r\n')
			return tokens[0].strip()
		return ""
		
#
#	Unitary actions
#

	def set_preset(self, preset_id):
		cmd = 'Preset.take = {0}'.format(int(preset_id))
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def get_configs_list(self):
		configs = []
		cmd = "ConfigList()"
		result = self.send_command(cmd, DEFAULT_EXPECT)  # result "Configs.Config1 = <...>\r\nConfigs.Config2 = <...>\r\nConfigs.Config3...\r\n"
		configs = self.convertTVONEListToJsonArray(result, True, True)
		return configs
		
	def get_config(self, config_id):
		cmd = 'Configs.Config{0}'.format( config_id )
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		result = self.convertTVONEListToJson(result)
		return result
		
	def save_config(self, config_id):
		cmd = 'Configs.Config{0}.Backup()'.format( config_id )
		self.send_command(cmd, DEFAULT_EXPECT) 
		
	def get_current_config_name(self):
		cmd = "System.ConfigName"
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		name = self.getTVONEValue(result)
		if not (name==""):
			return name
		return "unknown..."

	def load_config(self, config_id):
		cmd = 'Configs.Config{0}.Restore()'.format( config_id )
		self.send_command(cmd, DEFAULT_EXPECT) 
		
	def delete_config(self, config_id):
		cmd = 'Configs.Config{0}.Remove()'.format( config_id )
		self.send_command(cmd, DEFAULT_EXPECT) 

	def get_slots_list(self):
		result = {}
		cmd = 'Slots'
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		result = self.convertTVONEListToJsonList(result)
		return result
		
	def get_slot(self, slot_id):
		result = {}
		cmd = 'Slot{0}'.format( slot_id )
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		result = self.convertTVONEListToJsonList(result)
		return result

	def get_slot_in(self, slot_id, index):
		result = {}
		cmd = 'Slot{0}.In{1}'.format( slot_id, index )
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		result = self.convertTVONEListToJsonList(result)
		return result

	def get_slot_out(self, slot_id, index):
		result = {}
		cmd = 'Slot{0}.Out{1}'.format( slot_id, index )
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		result = self.convertTVONEListToJsonList(result)
		return result
		
	def get_windows_list(self):
		windows = []
		cmd = 'Windows'
		result = self.send_command(cmd, DEFAULT_EXPECT)  # result "Windows.Window1 = <...>\r\nWindows.Window2 = <...>\r\nWindows.Window3 = <...>\r\nWindows.Window4 = <...>\r\n"
		#result = "Windows.Window1 = <...>\r\nWindows.Window2 = <...>\r\nWindows.Window3 = <...>\r\nWindows.Window4 = <...>\r\n"
		windows = self.convertTVONEListToJsonArray(result, True, True)
		# retrieve name
		for window in windows:
			for key in window.keys():
				#print key, ": ", window[key]
				name = self.get_windows_name( key )
				window[key] = name
		return windows
		
	def get_windows_name(self, window_id):
		# First take Alias if it's available (i.e value is not "NULL")
		cmd = 'Window{0}.Alias'.format(window_id)
		result = self.send_command(cmd, DEFAULT_EXPECT)
		name = self.getTVONEValue(result);
		if name == "NULL":
			cmd = 'Window{0}.FullName'.format(window_id)
			result = self.send_command(cmd, DEFAULT_EXPECT)
			name = self.getTVONEValue(result);
		return name
		
	def get_window(self, window_id):
		result = {}
		cmd = 'Window{0}'.format( window_id )
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		result = self.convertTVONEListToJsonList(result)
		return result
		
	def set_window_width(self, window_id, w):
		cmd = 'Windows.window{0}.CanWidth = {1}'.format( window_id, w)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def get_window_width(self, window_id):
		cmd = 'Windows.window{0}.CanWidth'.format( window_id )
		result = self.send_command(cmd, DEFAULT_EXPECT)
		val = [int(s) for s in result.split() if s.isdigit()]
		return val[0]
		
	def set_window_height(self, window_id, h):
		cmd = 'Windows.window{0}.CanHeight = {1}'.format( window_id, h)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def get_window_height(self, window_id):
		cmd = 'Windows.window{0}.CanHeight'.format( window_id )
		result = self.send_command(cmd, DEFAULT_EXPECT)
		val = [int(s) for s in result.split() if s.isdigit()]
		return val[0]
		
	def set_window_x_position(self, window_id, x):
		cmd = 'Windows.window{0}.CanXCentre = {1}'.format( window_id, x)
		self.send_command(cmd, DEFAULT_EXPECT)

	def get_window_x_position(self, window_id):
		cmd = 'Windows.window{0}.CanXCentre'.format( window_id )
		result = self.send_command(cmd, DEFAULT_EXPECT)
		val = [int(s) for s in result.split() if s.isdigit()]
		return val[0]
		
	def set_window_y_position(self, window_id, y):
		cmd = 'Windows.window{0}.CanYCentre = {1}'.format( window_id, y)
		self.send_command(cmd, DEFAULT_EXPECT)

	def get_window_y_position(self, window_id):
		cmd = 'Windows.window{0}.CanYCentre'.format( window_id )
		result = self.send_command(cmd, DEFAULT_EXPECT)
		val = [int(s) for s in result.split() if s.isdigit()]
		return val[0]

	def set_window_zorder(self, window_id, z):
		cmd = 'Windows.window{0}.Zorder = {1}'.format( window_id, z)
		self.send_command(cmd, DEFAULT_EXPECT)

	def get_window_zorder(self, window_id):
		cmd = 'Windows.window{0}.Zorder'.format( window_id )
		result = self.send_command(cmd, DEFAULT_EXPECT)
		val = [int(s) for s in result.split() if s.isdigit()]
		return val[0]
		
	def set_window_rotation(self, window_id, angle):
		cmd = 'Windows.window{0}.RotateDeg = {1}'.format( window_id, angle)
		self.send_command(cmd, DEFAULT_EXPECT)

	def get_window_rotation(self, window_id):
		cmd = 'Windows.window{0}.RotateDeg'.format( window_id )
		result = self.send_command(cmd, DEFAULT_EXPECT)
		val = [int(s) for s in result.split() if s.isdigit()]
		return val[0]
		
	def set_window_border_pix_width(self, window_id, w):
		cmd = 'Windows.window{0}.BdrPixWidth = {1}'.format( window_id, w)
		self.send_command(cmd, DEFAULT_EXPECT)

	def set_window_border_color(self, window_id, color):
		cmd = 'Windows.window{0}.BdrRGB = {1}'.format( window_id, color)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_window_hflip(self, window_id, flag):
		switch = "Off"
		if( flag ):
			switch = "On"
		cmd = 'Windows.window{0}.HFlip = {1}'.format( window_id, switch)
		self.send_command(cmd, DEFAULT_EXPECT)

	def set_window_vflip(self, window_id, flag):
		switch = "Off"
		if( flag ):
			switch = "On"
		cmd = 'Windows.window{0}.VFlip = {1}'.format( window_id, switch)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_window_transition_fade(self, window_id, flag):
		switch = "Off"
		if( flag ):
			switch = "On"
		cmd = 'Windows.window{0}.SCFTB = {1}'.format( window_id, switch)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_window_transition_hshrink(self, window_id, flag):
		switch = "Off"
		if( flag ):
			switch = "On"
		cmd = 'Windows.window{0}.SCHShrink = {1}'.format( window_id, switch)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_window_transition_vshrink(self, window_id, flag):
		switch = "0"
		if( flag ): 
			switch = flag	# from -7 to 7
		cmd = 'Windows.window{0}.SCVShrink = {1}'.format( window_id, switch)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_window_transition_spin(self, window_id, flag):
		switch = "Off"
		if( flag ): 
			switch = "On"
		cmd = 'Windows.window{0}.SCSpin = {1}'.format( window_id, switch)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_window_input(self, window_id, slot_id, input_id):
		cmd = 'Windows.window{0}.Input = Slot{1}.In{2}'.format( window_id, slot_id, input_id)
		self.send_command(cmd, DEFAULT_EXPECT)
	
	def get_window_input(self, window_id):
		cmd = 'Windows.window{0}.Input'.format( window_id)
		result = self.send_command(cmd, DEFAULT_EXPECT)	# receive something as "Window1.Input = Slot3.In1 \n !Done Window1.Input"
		response = result.split()
		tab = re.findall(r'\d+', response[2])
		return (tab[0], tab[1]);
		
	def set_content_crop_left(self, slot, input_id, amount):
		cmd = 'Slot{0}.In{1}.LeftCrop = {2}'.format( slot, input_id, amount)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_content_crop_right(self, slot, input_id, amount):
		cmd = 'Slot{0}.In{1}.RightCrop = {2}'.format( slot, input_id, amount)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_content_crop_top(self, slot, input_id, amount):
		cmd = 'Slot{0}.In{1}.TopCrop = {2}'.format( slot, input_id, amount)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_content_crop_bottom(self, slot, input_id, amount):
		cmd = 'Slot{0}.In{1}.BottomCrop = {2}'.format( slot, input_id, amount)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def set_content_resolution(self, slot, input_id, resolution):
		cmd = 'Slot{0}.In{1}.Resolution = {2}'.format( slot, input_id, resolution)
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def get_content_resolution(self, slot, input_id):
		#cmd = 'Slot{0}.In{1}.Resolution'.format( slot, input_id)
		#return self.send_command(cmd, DEFAULT_EXPECT)
		cmd = 'Slot{0}.In{1}.Width'.format( slot, input_id)
		result = self.send_command(cmd, DEFAULT_EXPECT)	# receive something as "Slot14.Out1.Width = 1920 \n!Done Slot14.Out1.Width"
		val = [int(s) for s in result.split() if s.isdigit()]
		width = val[0]
		cmd = 'Slot{0}.In{1}.Height'.format( slot, input_id)
		result = self.send_command(cmd, DEFAULT_EXPECT)	
		val = [int(s) for s in result.split() if s.isdigit()]
		height = val[0]
		cmd = 'Slot{0}.In{1}.Field_Rate'.format( slot, input_id)
		result = self.send_command(cmd, DEFAULT_EXPECT)	
		val = [int(s) for s in result.split() if s.isdigit()]
		fps = val[0]
		return {'width': width, 'height': height, 'fps': fps };
		
	def play_content(self, slot, input_id, uri):
		input = "127.0.0.1:8080"
		url = "http://" + input + "/requests/status.xml?command=in_play&input=" + uri
		r = requests.get(url, auth=('', 'toto'))
		
	def stop_content(self, slot, input_id):
		input = "127.0.0.1:8080"
		url = "http://" + input + "/requests/status.xml?command=pl_stop"
		r = requests.get(url, auth=('', 'toto'))
		
	def get_inputs_list(self):
		# Get the slots list
		slots = []
		cmd = 'Slots'
		result = self.send_command(cmd, DEFAULT_EXPECT)	# receive list
		# split response in multiline
		inputlist = result.split('\n')
		# then get the list of slots number with no "NO CARD"
		for slot in inputlist:
			if not "NO CARD" in slot:
				tab = re.findall(r'\d+', slot)
				slots.append( tab[0] )
		return slots
		
	def get_presets_list(self):
		# Get the presets list
		presets = []
		cmd = 'Preset.PresetList()'
		result = self.send_command(cmd, DEFAULT_EXPECT)	# receive list 'Routing.Preset.PresetList[1]=Background,Canvas1,1000\r\nRouting.Preset.PresetList[2]=Movie,Canvas1,0\r\nRouting.Preset.PresetList[3]=Monitoring_All_SRC,Canvas4,0\r\nRouting.Preset.PresetList[4]=Monitoring_One_SRC,Canvas4,0\r\nRouting.Preset.PresetList[5]=CL,Canvas1,3000\r\nRouting.Preset.PresetList[6]=Whiteboard,Canvas1,1000\r\nRouting.Preset.PresetList[7]=Control_Room_slides,Canvas1,1000\r\n!Done '
		# split response in multiline
		presetList = result.split('\n')
		# then get the list of presets number
		for preset in presetList:
			tokens = preset.split('=')
			if( len(tokens) > 1 ):
				tab = re.findall(r'\d+', tokens[0])
				presets.append( {tab[0]:tokens[1]} )
		return presets
				
	def get_active_preset(self):
		cmd = 'Preset.Take'
		result = self.send_command(cmd, DEFAULT_EXPECT)
		val = [int(s) for s in result.split() if s.isdigit()]
		return val[0]
		
	def set_active_preset(self, preset_id):
		cmd = 'Preset.Take = {0}'.format( preset_id)
		self.send_command(cmd, DEFAULT_EXPECT)

	def save_active_preset(self):
		cmd = 'Preset.SaveRead()'
		self.send_command(cmd, DEFAULT_EXPECT)
		
	def get_canvases_list(self):
		canvases = []
		cmd = 'Canvases'
		result = self.send_command(cmd, DEFAULT_EXPECT)  
		canvasList = result.split('\n')
		for canvas in canvasList:
			tab = re.findall(r'\d+', canvas)
			if( len(tab) > 0 ):
				canvases.append( int(tab[0]) )
		return canvases
		
	def get_canvas(self, canvas_id):
		cmd = 'Canvas{0}'.format( canvas_id )
		result = self.send_command(cmd, DEFAULT_EXPECT) 
		result = self.convertTVONEListToJson(result)
		return result

	def get_windows_on_canvas(self, canvas_id):
		windows = []
		canvas = self.get_canvas( canvas_id )
		#extract windows list
		value = canvas['WindowList']
		tokens = value.split(',')
		for token in tokens:
			tab = re.findall(r'\d+', token)
			if( len(tab) > 0 ):
				windows.append( int(tab[0]) )

		return windows

#
#	aPI
#
	
	def set_window_size(self, window_id, x, y, w, h):
		self.set_window_width(window_id, w)
		self.set_window_height(window_id, h)
		self.set_window_x_position(window_id, x)
		self.set_window_y_position(window_id, y)
		
	def move_window(self, window_id, delta_x, delta_y):
		print 'move_window: ' + repr(delta_x) + ", "+ repr(delta_y)
		x = self.get_window_x_position(window_id);
		self.set_window_x_position(window_id, x+delta_x)
		y = self.get_window_y_position(window_id);
		print 'move_window: y=' + repr(y) + ", delta_y="+ repr(delta_y)
		self.set_window_y_position(window_id, y+delta_y)
		
	def rotate_window(self, window_id, delta_a):
		a = self.get_window_rotation(window_id);
		self.set_window_rotation(window_id, a+delta_a)

	def set_window_border(self, window_id, w, color):
		self.set_window_border_pix_width(window_id, w)
		self.set_window_border_color(window_id, color)

	def set_window_effect(self, window_id, effects_array):
		for effect in effects_array:
			if effect == "fade":
				self.set_window_transition_fade(window_id, True)
			elif effect == "hshrink":
				self.set_window_transition_hshrink(window_id, True)
			elif effect == "vshrink":
				self.set_window_transition_vshrink(window_id, True)
			elif effect == "spin":
				self.set_window_transition_spin(window_id, 1)
	
	def set_crop(self, window_id, l, r, t, b):
		slot_id, input_id = self.get_window_input(window_id)
		self.set_content_crop_left(slot_id, input_id, l)
		self.set_content_crop_left(slot_id, input_id, r)
		self.set_content_crop_left(slot_id, input_id, t)
		self.set_content_crop_left(slot_id, input_id, b)
		
	def set_window_quality(self, window_id, q):
		slot_id, input_id = self.get_window_input(window_id)
		if q == "low":
			self.set_content_resolution(slot_id, input_id, "640x480p60")
		elif q == "medium":
			self.set_content_resolution(slot_id, input_id, "1280x720p60")
		elif q == "high":
			self.set_content_resolution(slot_id, input_id, "1920x1080p60")
		