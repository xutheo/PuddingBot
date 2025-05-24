import datetime
import os
from sqlitedict import SqliteDict

sqlitedict_base_path = f"/mnt/timeline_data/test_"
if os.environ['COMPUTERNAME'] == 'ZALTEO' or os.environ['COMPUTERNAME'] == 'LAPTOP-RVEEJPKP':
    sqlitedict_base_path = f"./mnt/timeline_data/test_"


dtier_sheet_ids = {
    1: "1305029905",
    2: "1699807028",
    3: "1464210928",
    4: "2047017564",
    5: "311078222"
}

score_multipliers = {
    1: 4.5,
    2: 4.5,
    3: 4.8,
    4: 4.8,
    5: 5
}

dtier_simple_sheet_id = 1391911131
dtier_ots_id = 835537673
bosses_info_id = 1709504644

#sheet_id = "1IvRAi0hh7-PehhD7jaeXU-OX6CU_oaAl6Sy5JKkIV90"
test_sheet_id = "1IvRAi0hh7-PehhD7jaeXU-OX6CU_oaAl6Sy5JKkIV90"

translation_sheet_id = '11B6-6mmQC4XMTiSadrfKGlS_y4qSnLzfFHj1_W8XLhI'

#homework_sheet_id = '1UClOlALY5x7Jr3DMHoheSW3_Of1ToPRjfdA5VahWaQQ'
#chorry_homework_sheet_id = '1FiVC_y4LOES6wIGN8591HZrwiSxejmAgXRNLzML_0ak'
homework_sheet_gid = '574547770'

roster_sheet_id = '15GBJagkAmLY70IiXwxce5VKWeSOioDfVoxrU-MxpqBo'
chorry_roster_sheet_id = '1upz1usqd3abQ07WSR0zXyJUVBsw6tQ9t08w8GFvv224'
borry_roster_sheet_id = ''

metrics_sheet_id = '1G0oY2lQIAAVxDuFBQQSKYsREzqb31Q_t7CENUzdxyAQ'
metrics_gid = 0
metrics_test_gid = 49006389

roster_users = {
    'Dabomstew': 'dBONKs',
    'Astordor': 'Altstordor',
    'Dragonofhonor': 'Dragon',
    'Fae': 'Faefeedge',
    'Tomoeri': 'TomoP',
    'Kami': 'Shirou',
    'TakamoriXD': 'Takamori2'
}

cb_info_dict = SqliteDict(sqlitedict_base_path + 'clanbattle.sqlite', autocommit=True)

boss_image_urls = SqliteDict(sqlitedict_base_path + 'bossinfo.sqlite', autocommit=True)

boss_image_urls_to_add = {
    "Wyvern": "https://redive.estertion.win/icon/unit/302100.webp",
    "Wild Gryphon": "https://redive.estertion.win/icon/unit/302000.webp",
    "Dirtigator": "https://redive.estertion.win/icon/unit/309100.webp",
    "Titanoturtle": "https://redive.estertion.win/icon/unit/304100.webp",
    "Karkinos": "https://redive.estertion.win/icon/unit/302700.webp",
    "Goblin Brave": "https://redive.estertion.win/icon/unit/305700.webp",
    "Rai-Rai": "https://redive.estertion.win/icon/unit/304600.webp",
    "Smoldersaurus": "https://redive.estertion.win/icon/unit/303600.webp",
    "Flower Madonna": "https://redive.estertion.win/icon/unit/319200.webp",
    "Orleon": "https://redive.estertion.win/icon/unit/302800.webp",
    "Toughgeist": "https://redive.estertion.win/icon/unit/320800.webp",
    "Wraithlord": "https://redive.estertion.win/icon/unit/304800.webp",
    "Spirit Horn": "https://redive.estertion.win/icon/unit/300800.webp",
    "Medusa": "https://redive.estertion.win/icon/unit/301400.webp",
    "Greater Golem": "https://redive.estertion.win/icon/unit/301200.webp",
    "Land Sloth": "https://redive.estertion.win/icon/unit/309000.webp",
    "Venom Salamandra": "https://redive.estertion.win/icon/unit/306600.webp",
    "Dark Gargoyle": "https://redive.estertion.win/icon/unit/315600.webp",
    "Glutton": "https://redive.estertion.win/icon/unit/301300.webp",

    "Madam Electra": "https://redive.estertion.win/icon/unit/312500.webp",
    "Goblin Rider": "https://redive.estertion.win/icon/unit/316600.webp",
    "Wild Talon": "https://redive.estertion.win/icon/unit/306400.webp",
    "Ziz": "https://redive.estertion.win/icon/unit/301600.webp",
    "Lesathapult": "https://redive.estertion.win/icon/unit/300200.webp",

    "Mega Lapahn": "https://redive.estertion.win/icon/unit/305100.webp",
    "Sagitarius": "https://redive.estertion.win/icon/unit/301800.webp",
    "Flower Chevalier": "https://redive.estertion.win/icon/unit/311200.webp",
    "Frost Hound": "https://redive.estertion.win/icon/unit/319600.webp",

    "Needle Creeper": "https://redive.estertion.win/icon/unit/300600.webp",
    "Basilisk Allos": "https://redive.estertion.win/icon/unit/321900.webp",
    "Aquarius": "https://redive.estertion.win/icon/unit/302900.webp",
    "Algedi": "https://redive.estertion.win/icon/unit/300400.webp",
    "Obsidian Wyvern": "https://redive.estertion.win/icon/unit/312000.webp",
    "Mushussu": "https://redive.estertion.win/icon/unit/303500.webp"
}

def save_sheet_id(id):
    cb_info_dict['sheet_id'] = id


def get_sheet_id():
    key = 'sheet_id'
    return cb_info_dict[key]


def save_homework_sheet_id(id, clan='Worry'):
    if clan == 'Worry':
        cb_info_dict['hw_sheet_id'] = id
    elif clan == 'Chorry':
        cb_info_dict['hw_chorry_sheet_id'] = id
    elif clan == 'Borry':
        cb_info_dict['hw_borry_sheet_id'] = id

#save_homework_sheet_id('1Jbv7YLunoHza472-Iel2HkGfSgyFO-Bj8OtcfHW-R3A')
#save_homework_sheet_id('1FiVC_y4LOES6wIGN8591HZrwiSxejmAgXRNLzML_0ak', chorry=True)

def get_homework_sheet_id(clan='Worry'):
    key = 'hw_sheet_id' if clan == 'Worry' else 'hw_chorry_sheet_id' if clan == 'Chorry' else 'hw_borry_sheet_id'
    if key not in cb_info_dict:
        return '1UClOlALY5x7Jr3DMHoheSW3_Of1ToPRjfdA5VahWaQQ' if clan == 'Worry' else '1zBsH7fdeVf6mhCk7P3FJAm2EDbGuMn2aY7cw0xsEhyc'
    return cb_info_dict[key]


def get_boss_names():
    if 'boss_names' not in cb_info_dict:
        return {1: None, 2: None, 3: None, 4: None, 5: None}
    return cb_info_dict['boss_names']


def save_boss_name(boss, name):
    names = get_boss_names()
    names[int(boss)-1] = name
    cb_info_dict['boss_names'] = names

    if name in boss_image_urls:
        boss_urls = get_boss_urls()
        boss_urls[int(boss) - 1] = boss_image_urls[name]
        cb_info_dict['boss_urls'] = boss_urls


def get_boss_urls():
    if 'boss_urls' not in cb_info_dict:
        return {1: None, 2: None, 3: None, 4: None, 5: None}
    return cb_info_dict['boss_urls']


def save_time(year, month, day, hour, start=True):
    if start:
        cb_info_dict['cb_start_time'] = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
    else:
        cb_info_dict['cb_end_time'] = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)


def get_time(start=True):
    if start and 'cb_start_time' in cb_info_dict:
        return cb_info_dict['cb_start_time']
    elif (not start) and 'cb_end_time' in cb_info_dict:
        return cb_info_dict['cb_end_time']


def find_current_day():
    current = datetime.datetime.now(datetime.timezone.utc)
    day = 1
    cb_start_time = get_time(True)
    cb_end_time = get_time(False)
    start = cb_start_time + datetime.timedelta(days=1)
    while start < current:
        if start >= cb_end_time:
            break
        day += 1
        start += datetime.timedelta(days=1)
    return day

'''
boss_names = {
    1: "Goblin",
    2: "Gryphon",
    3: "Sea Drake",
    4: "Ulfhedinn",
    5: "Torpedon"
}

cb_start_time = datetime.datetime(2024, 6, 24, 20, tzinfo=datetime.timezone.utc)
cb_end_time = datetime.datetime(2024, 6, 29, 8, tzinfo=datetime.timezone.utc)'''
#save_homework_sheet_id("1kN54HGKnRoMGYWFDTTFq4CqTTg_kcyVUyp2ZCMY5bUc", chorry=True)