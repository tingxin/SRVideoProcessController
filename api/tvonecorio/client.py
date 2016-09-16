
# client.py		: 	tvonecorio communication manager

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

screens = [
	{'id': 1,
	 'name': 'left',
	 'description': 'Left screen',
	 'videoproc': {'host': '192.168.0.2', 'user': 'admin', 'password': 'adminpw'},
	 'monitorsX': 4,
	 'monitorsY': 3},
	{'id': 2,
	 'name': 'right',
	 'description': 'Right screen',
	 'videoproc': {'host': '192.168.0.3', 'user': 'admin', 'password': 'adminpw'},
	 'monitorsX': 3,
	 'monitorsY': 3}
]

connections = {}

def corio_get(screen):
	global connections

	videoproc = screen['videoproc']
	if screen['id'] not in connections:
		#try:
		c = Client(videoproc['host'], user=videoproc['user'], password=videoproc['password'])
		connections[screen['id']] = c
		#except:
		#    abort(503)
		#    return None
	return connections[screen['id']]


def	corio_send_command(screen_id, command):
	screen = [screen for screen in screens if screen['id'] == screen_id]
	if len(screen) == 0:
		return make_ERROR_response_with_content( "Can't find screen with id '"+repr(screen_id)+"'" )
	c = corio_get( screen[0] )
	return c.send_command( command, DEFAULT_EXPECT )

def	corio_send_batchcommands(screen_id, commands):
	screen = [screen for screen in screens if screen['id'] == screen_id]
	if len(screen) == 0:
		return make_ERROR_response_with_content( "Can't find screen with id '"+repr(screen_id)+"'" )
	c = corio_get( screen[0] )
	c.send_command( "StartBatch", DEFAULT_EXPECT )
	for cmd in commands:
		c.send_command( cmd, DEFAULT_EXPECT )
	c.send_command( "EndBatch ", DEFAULT_EXPECT )

def corio_get_screens():
	return screens


def corio_get_screen(screen_id):
	screen = [screen for screen in screens if screen['id'] == screen_id]
	return screen

def corio_get_screen_by_name(screen_name):
	screen = [screen for screen in screens if screen['name'] == screen_name]
	return screen


def corio_get_connections():
	conns = []
	for screen_id, conn in connections.items():
		conns.append({'screen_id': screen_id, 'connected': conn.connected()})
	return conns


def corio_release_connections():
	global connections
	conns = []
	for screen_id, conn in connections.items():
		if conn.connected() is True:
			screen = corio_get_screen( screen_id )
			if len(screen) == 0:
				return make_ERROR_response_with_content( "Can't find screen with id '"+repr(screen_id)+"'" )
			c = corio_get( screen[0] )
			try:
				c.close()
			except Exception, e:
				return make_ERROR_response_with_content( repr(e) )
			conns.append({'screen_id': screen_id, 'connection': 'closed'})
	connections = {}
	return conns


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
		try:
			if self.logged:
				self.connection.write('logout\n')
		except:
			print "can't close connection gracefully: " + repr(result)
		try:
			self.connection.close()
		except:
			print "can't close connection : " + repr(result)
		self.logged = False


	def send_command(self, command, expected=None):
		response = ""

		if not self.logged:
			self.login()
		result = self.connection.write(command + '\n')
		#print "connection write=" + repr(result)

		if expected is not None:
			# the end is "!Done <cmd>\r\n" or "!Error ... <cmd>\r\n"
			expected = "!(.*) " + re.escape(command) + "\r\n"	# '!(.*) Slot4\\.In1\\.Width\r\n' Don't recognize "!Error -113 : Unrecognised Field name\r\n// Slot4.In1.Width\r\n"
			#print "connection expcted="+repr(expected)
			try:
				index, obj, response = self.connection.expect( [re.compile(expected)], 1.0 )
				#print "connection index="+repr(index) + ", obj="+repr(obj) + ", response=" + repr(response)
			except EOFError, e:
				print "Exception: e="+repr(e)

		return response
