# scenarios.py	:	scenarios management module

import tools
import database


def get_scenarios_list():
    return database.get_scenarios_list()

def create_scenario(name, left_preset, right_preset, audio_src, audio_lvl, duration):
    database.create_scenario( name, left_preset, right_preset, audio_src, audio_lvl, duration )
    return "ok"

def delete_scenario(id):
    database.delete_scenario(id)
    return "ok"

def update_scenario(id, name, left_preset, right_preset, audio_src, audio_lvl, duration):
    database.update_scenario(id, name, left_preset, right_preset, audio_src, audio_lvl, duration)
    return "ok"
