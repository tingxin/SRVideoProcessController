import sqlite3
from flask import g

DATABASE = 'immersive.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect( DATABASE )
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS scenarios ("
                        "id integer primary key not null, "
                        "name text, "
                        "left_preset int, "
                        "right_preset int, "
                        "audio_src text, "
                        "audio_lvl int, "
                        "duration int)")
        db.commit()
        cursor.execute("CREATE TABLE IF NOT EXISTS inputs ("
                        "slot text, "
                        "name text, "
                        "wall_id int, "
                        "touch_ctrl text, "
                        "pict_name text, "
                        "video_ctrl text)")
        db.commit()
    return db

def close_database():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#
#
#   Scenarios management
#
#
def get_scenarios_list():
    sql = "SELECT * FROM scenarios"
    cursor = get_db().cursor()
    cursor.execute( sql )
    values = []
    for row in cursor:
        value = {'id': row[0],'name': row[1], 'left_preset': row[2], 'right_preset': row[3], 'audio_src': row[4], 'audio_lvl': row[5], 'duration': row[6]}
        values.append( value )
    return values

def create_scenario(name, left_preset, right_preset, audio_src, audio_lvl, duration):
    tuple_data = (name, left_preset, right_preset, audio_src, audio_lvl, duration)
    sql = "INSERT INTO scenarios (name, left_preset, right_preset, audio_src, audio_lvl, duration) VALUES (?,?,?,?,?,?)";
    cursor = get_db().cursor()
    cursor.execute(sql, tuple_data)
    get_db().commit()

def delete_scenario(id):
    sql = "DELETE FROM scenarios WHERE id={0}".format(id)
    cursor = get_db().cursor()
    cursor.execute( sql )
    get_db().commit()

def update_scenario(id, name, left_preset, right_preset, audio_src, audio_lvl, duration):
    sql = "UPDATE scenarios SET name='{1}', left_preset={2}, right_preset={3}, audio_src='{4}', audio_lvl={5}, duration={6} WHERE id={0}" \
            .format(id, name, left_preset, right_preset, audio_src, audio_lvl, duration)
    cursor = get_db().cursor()
    cursor.execute( sql )
    get_db().commit()

#
#
#   Inputs management
#
#
def get_input_by_slot(slot_txt, wall_id):
    sql = "SELECT * FROM inputs WHERE slot='{0}' AND wall_id={1}".format( slot_txt, wall_id )
    cursor = get_db().cursor()
    cursor.execute( sql )
    values = []
    for row in cursor:
        value = {'slot': row[0], 'name': row[1], 'wall_id': row[2], 'touch_ctrl': row[3], 'pict_name': row[4], 'video_ctrl': row[5]}
        values.append( value )
    return values

def create_input(slot_txt, name_txt, wall_id, touch_txt, pict_txt, video_txt):
    tuple_data = (slot_txt, name_txt, wall_id, touch_txt, pict_txt, video_txt)
    sql = "INSERT INTO inputs (slot, name, wall_id, touch_ctrl, pict_name, video_ctrl) VALUES (?,?,?,?,?,?)";
    cursor = get_db().cursor()
    cursor.execute( sql, tuple_data )
    get_db().commit()

def update_input_name(slot_txt, wall_id, name_txt):
    sql = "UPDATE inputs SET name='{2}' WHERE slot='{0}' AND wall_id={1}".format( slot_txt, wall_id, name_txt )
    cursor = get_db().cursor()
    cursor.execute( sql )
    get_db().commit()
def update_input_touch_ctrl(slot_txt, wall_id, touch_txt):
    sql = "UPDATE inputs SET touch_ctrl='{2}' WHERE slot='{0}' AND wall_id={1}".format( slot_txt, wall_id, touch_txt )
    cursor = get_db().cursor()
    cursor.execute( sql )
    get_db().commit()
def update_input_pict_name(slot_txt, wall_id, pict_txt):
    sql = "UPDATE inputs SET pict_name='{2}' WHERE slot='{0}' AND wall_id={1}".format( slot_txt, wall_id, pict_txt )
    cursor = get_db().cursor()
    cursor.execute( sql )
    get_db().commit()
def update_input_video_ctrl(slot_txt, wall_id, video_txt):
    sql = "UPDATE inputs SET video_ctrl='{2}' WHERE slot='{0}' AND wall_id={1}".format( slot_txt, wall_id, video_txt )
    cursor = get_db().cursor()
    cursor.execute( sql )
    get_db().commit()

def get_inputs_alias_list():
    sql = "SELECT * FROM inputs"
    cursor = get_db().cursor()
    cursor.execute( sql )
    values = []
    for row in cursor:
        value = {'slot': row[0], 'name': row[1], 'wall_id': row[2], 'touch_ctrl': row[3], 'pict_name': row[4], 'video_ctrl': row[5]}
        values.append( value )
    return values
