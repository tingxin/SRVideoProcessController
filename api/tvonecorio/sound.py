
# sound.py	:	Sound management module
# -*- coding: utf-8 -*-

import requests
from lxml import etree

SOUND_BASE = "http://192.168.0.9/YamahaRemoteControl/ctrl"
SETTINGS_URI = """<?xml version="1.0" encoding="utf-8"?><YAMAHA_AV cmd="GET"><Main_Zone><Basic_Status>GetParam</Basic_Status></Main_Zone></YAMAHA_AV>"""

def sound_set_input( input ):
    payload = """<?xml version="1.0" encoding="utf-8"?><YAMAHA_AV cmd="PUT"><Main_Zone><Input><Input_Sel>{0}</Input_Sel></Input></Main_Zone></YAMAHA_AV>""".format(input)
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    print repr( r.text )

def sound_up():
    payload = """<?xml version="1.0" encoding="utf-8"?><YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>Up 2 dB</Val><Exp></Exp><Unit></Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>"""
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    print repr( r )

def sound_down():
    payload = """<?xml version="1.0" encoding="utf-8"?><YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>Down 2 dB</Val><Exp></Exp><Unit></Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>"""
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    print repr( r )

def sound_mute():
    #payload = """<?xml version="1.0" encoding="utf-8"?><YAMAHA_AV cmd="GET"><Main_Zone><Basic_Status>GetParam</Basic_Status></Main_Zone></YAMAHA_AV>"""
    payload = """<?xml version="1.0" encoding="utf-8"?><YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Mute>On</Mute></Volume></Main_Zone></YAMAHA_AV>"""
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    print r.text

def sound_unmute():
    payload = """<?xml version="1.0" encoding="utf-8"?><YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Mute>Off</Mute></Volume></Main_Zone></YAMAHA_AV>"""
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    print r.text

def sound_get_muted():
    payload = SETTINGS_URI
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    xml = etree.XML(r.text)
    muteElmt = xml.find("./Main_Zone/Basic_Status/Volume/Mute")
    return muteElmt.text

def sound_get_input():
    payload = SETTINGS_URI
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    xml = etree.XML(r.text)
    srcElmt = xml.find("./Main_Zone/Basic_Status/Input/Input_Sel")
    return srcElmt.text

def api_sound_get_settings():
    payload = SETTINGS_URI
    headers = {'Content-Type': 'application/xml'}
    r = requests.post(SOUND_BASE, data=payload, headers=headers)
    xml = etree.XML(r.text)
    muteElmt = xml.find("./Main_Zone/Basic_Status/Volume/Mute")
    srcElmt = xml.find("./Main_Zone/Basic_Status/Input/Input_Sel")
    return { "mute": muteElmt.text, "src": srcElmt.text }
