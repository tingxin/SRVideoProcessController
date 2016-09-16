import sqlite3
import os

DATABASE = 'immersive.db'
DATABASE_OLD = 'immersive.db.old'

if os.path.exists(DATABASE_OLD):
    os.remove(DATABASE_OLD)
if os.path.exists(DATABASE):
    os.rename(DATABASE, DATABASE_OLD)

db = sqlite3.connect( DATABASE )
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


staticScenarios =  [
        {"id": 0, "name":"Backgrounds",         "left_preset":26, "right_preset":8,  "audio_src":"AUDIO1", "audio_lvl": 0, "duration": 0},
        {"id": 1, "name":"Connected Life",      "left_preset":5,  "right_preset":5,  "audio_src":"AUDIO1", "audio_lvl": 0, "duration": 0},
        {"id": 2, "name":"Movie",               "left_preset":34, "right_preset":-1, "audio_src":"AUDIO4", "audio_lvl": 0, "duration": 0},
        {"id": 3, "name":"Telepresence",        "left_preset":-1, "right_preset":9,  "audio_src":"AUDIO1", "audio_lvl": 0, "duration": 0},
        {"id": 4, "name":"Snowflake",           "left_preset":33, "right_preset":10, "audio_src":"AUDIO1", "audio_lvl": 0, "duration": 0},
        {"id": 4, "name":"Whiteboard + 6lab",   "left_preset":29, "right_preset":9,  "audio_src":"AUDIO1", "audio_lvl": 0, "duration": 0},
        {"id": 5, "name":"Whiteboard + SPA",    "left_preset":31, "right_preset":9,  "audio_src":"AUDIO1", "audio_lvl": 0, "duration": 0},
        {"id": 6, "name":"e-valley intro",      "left_preset":33, "right_preset":8,  "audio_src":"AUDIO1", "audio_lvl": 0, "duration": 0},
        {"id": 6, "name":"e-valley",            "left_preset":2,  "right_preset":8,  "audio_src":"AUDIO4", "audio_lvl": 0, "duration": 0},
    ]
for row in staticScenarios:
    tuple_data = (row["name"], row["left_preset"], row["right_preset"], row["audio_src"], row["audio_lvl"], row["duration"])
    sql = "INSERT INTO scenarios (name, left_preset, right_preset, audio_src, audio_lvl, duration) VALUES (?,?,?,?,?,?)";
    cursor = db.cursor()
    cursor.execute(sql, tuple_data)
    db.commit()

staticsInputs = [
        {"slot": "Slot5.In1", "name": "NUC1",   "wall_id": 1, "touchctrl": "192.168.56.1", "pictname": "./thumbnail/1_Slot5.In1.png", "videoctrl": "192.168.56.1:8080"},
        {"slot": "Slot3.In1", "name": "Devnet", "wall_id": 1, "touchctrl": "10.60.6.22", "pictname": "./thumbnail/1_Slot3.In1.png", "videoctrl": "10.60.6.22:8080"},
        {"slot": "Slot3.In2", "name": "NUC4",   "wall_id": 1, "touchctrl": "10.60.6.22", "pictname": "./thumbnail/1_Slot3.In2.png", "videoctrl": "10.60.6.22:8080"},
        {"slot": "Slot1.In1", "name": "NUC1",   "wall_id": 1, "touchctrl": "10.60.6.23", "pictname": "./thumbnail/1_Slot1.In1.png", "videoctrl": "10.60.6.23:8080"},
        {"slot": "Slot2.In1", "name": "NUC3",   "wall_id": 1, "touchctrl": "10.60.6.25", "pictname": "./thumbnail/1_Slot2.In1.png", "videoctrl": "10.60.6.25:8080"},
        {"slot": "Slot1.In2", "name": "NUC2",   "wall_id": 1, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/1_Slot1.In2.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot4.In2", "name": "Connected life", "wall_id": 1, "touchctrl": "10.60.6.25", "pictname": "./thumbnail/1_Slot4.In2.png", "videoctrl": "10.60.6.25:8080"},
        {"slot": "Slot4.In1", "name": "Connected life", "wall_id": 1, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/1_Slot4.In1.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot6.In1", "name": "Whiteboard",     "wall_id": 1, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/1_Slot6.In1.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot4.In1", "name": "Connected life", "wall_id": 2, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/2_Slot4.In1.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot6.In1", "name": "Whiteboard",     "wall_id": 2, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/2_Slot6.In1.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot1.In1", "name": "T.P.",           "wall_id": 2, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/2_Slot1.In1.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot5.In1", "name": "Background SFO", "wall_id": 2, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/2_Slot5.In1.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot6.In2", "name": "Background Paris", "wall_id": 1, "touchctrl": "10.60.6.24", "pictname": "./thumbnail/1_Slot6.In2.png", "videoctrl": "10.60.6.24:8080"},
        {"slot": "Slot3.In2", "name": "Alien Snowflake",  "wall_id": 2, "touchctrl": "192.168.0.157", "pictname": "./thumbnail/2_Slot3.In2.png", "videoctrl": "192.168.0.157:8080"},
]
for row in staticsInputs:
    tuple_data = (row["slot"], row["name"], row["wall_id"], row["touchctrl"], row["pictname"], row["videoctrl"])
    sql = "INSERT INTO inputs (slot, name, wall_id, touch_ctrl, pict_name, video_ctrl) VALUES (?,?,?,?,?,?)";
    cursor = db.cursor()
    cursor.execute( sql, tuple_data )
    db.commit()
