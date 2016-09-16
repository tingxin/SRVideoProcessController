
# slots.py	:	Slots management module

import client
import tools
import database

def get_slots_list(screen_id):
    result = {}
    cmd = 'Slots'
    result = client.corio_send_command(screen_id, cmd)
    result = tools.convertTVONEListToJsonList(result, True, True)
    return result

def get_slot(screen_id, slot_id):
    result = {}
    cmd = 'Slot{0}'.format( slot_id )
    result = client.corio_send_command(screen_id, cmd)
    result = tools.convertTVONEListToJsonList(result)
    return result

def get_slot_in(screen_id, slot_id, index):
    result = {}
    cmd = 'Slot{0}.In{1}'.format( slot_id, index )
    result = client.corio_send_command(screen_id, cmd)
    result = tools.convertTVONEListToJsonList(result)
    return result

def get_slot_in_image(screen_id, slot_id, index):
    default_image = "./thumbnail/unk.png"
    slot_name = 'Slot{0}.In{1}'.format( slot_id, index )
    image = get_input_pict_name( screen_id, slot_name )
    if image != "":
        return image
    return default_image

def get_slot_out(screen_id, slot_id, index):
    result = {}
    cmd = 'Slot{0}.Out{1}'.format( slot_id, index )
    result = client.corio_send_command(screen_id, cmd)
    result = tools.convertTVONEListToJsonList(result)
    return result

def get_inputs_slots_list(screen_id):
    result = {}

    # First: get list of all slots
    cmd = 'Slots'
    result = client.corio_send_command(screen_id, cmd)
    result = tools.convertTVONEListToJsonList(result, True, True)

    # then get only slots not empty
    slots_filled = []
    for slot in result:
        if result[slot] != "NO CARD":
            slots_filled.append(slot);

    # then for each slots, take only input slots
    input_slots = []
    for slot in slots_filled:
        result = {}
        cmd = 'Slot{0}'.format( slot )
        result = client.corio_send_command(screen_id, cmd)
        result = tools.convertTVONEListToJsonList( result )
        for param in result:
            if param.startswith('In') and result[param]=="<...>" :
                slot_name = 'Slot{0}.In{1}'.format( slot, param[2])
                alias = get_input_alias( screen_id, slot_name )
                image = get_input_pict_name( screen_id, slot_name )
                input_slots.append( {'name': slot_name, 'alias': alias, 'pict': image} )

    return input_slots


# return an alias (if exists) from the config corresponding to the slot name (i.e. "Slot<x>.In<y>")
def get_input_alias( screen_id, slot_name ):
    inputs = database.get_input_by_slot(slot_name, screen_id)
    if len( inputs ) > 0:
        return inputs[0]["name"]
    return ""

# return the thumbnail (if exists) from the config corresponding to the slot name (i.e. "Slot<x>.In<y>")
def get_input_pict_name( screen_id, slot_name ):
    inputs = database.get_input_by_slot(slot_name, screen_id)
    if len( inputs ) > 0:
        return inputs[0]["pict_name"]
    return ""
