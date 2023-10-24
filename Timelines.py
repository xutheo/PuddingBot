from sqlitedict import SqliteDict
import sheets_helper
from clan_battle_info import dtier_sheet_ids, boss_names, boss_image_urls, dtier_simple_sheet_id
import os
import threading
import time
from threading import Lock

load_to_db_lock = Lock()
sqlitedict_base_path = f"/mnt/timeline_data/test_"
if os.environ['COMPUTERNAME'] == 'ZALTEO':
    sqlitedict_base_path = f"./mnt/timeline_data/test_"


class Timeline:
    UNIT_NAME_ROW = 2
    UNIT_LEVEL_ROW = 7
    UNIT_RANK_ROW = 8
    UNIT_STAR_ROW = 9
    UNIT_UE_ROW = 10

    TL_START_ROW = 15
    TL_COL_LABELS_ROW = 13
    TL_STARTING_SET_ROW = 14

    SIMPLE_UNIT_NAME_ROW = 2
    SIMPLE_UNIT_LEVEL_ROW = 6
    SIMPLE_UNIT_RANK_ROW = 7
    SIMPLE_UNIT_STAR_ROW = 8
    SIMPLE_UNIT_UE_ROW = 9

    def __init__(self, tl_data, boss, tl_cell_tuple, simple):
        if not simple:
            self.id = tl_data[0][0]
            self.sheet_id = dtier_sheet_ids[boss]
            self.author = "" if not tl_data[0][1] else \
                tl_data[0][1].split('Original Author: ')[1] if 'Original Author: ' in tl_data[0][1] else ''
            self.transcriber = "" if not tl_data[1][1] else \
                tl_data[1][1].split('by ')[1] if 'by ' in tl_data[1][1] else ''
            self.ev = tl_data[1][7]
            self.st_dev = tl_data[2][7]
            self.style = tl_data[4][0]
            self.status = tl_data[6][0]
            self.units = []
            for i in range(5):
                unit = Unit(tl_data[self.UNIT_NAME_ROW][i + 1],
                            tl_data[self.UNIT_LEVEL_ROW][i + 1],
                            tl_data[self.UNIT_RANK_ROW][i + 1],
                            tl_data[self.UNIT_STAR_ROW][i + 1],
                            tl_data[self.UNIT_UE_ROW][i + 1])
                self.units.append(unit)
            tl_end_row = len(tl_data)
            self.tl_labels = list(filter(None, tl_data[self.TL_COL_LABELS_ROW]))
            if self.tl_labels[1] == 'Unit':
                self.unit_column = True
            else:
                self.unit_column = False
            self.starting_set_status = list(filter(None, tl_data[self.TL_STARTING_SET_ROW]))
            self.tl_actions = tl_data[self.TL_START_ROW:tl_end_row - 2]
            labels_length = len(self.tl_labels)
            actions_length = len(self.tl_actions[0])
            for tl_action in self.tl_actions:
                del tl_action[labels_length - 2: actions_length - 2]
            self.simple = False
        else:
            self.id = tl_data[0][0]
            self.sheet_id = dtier_simple_sheet_id
            self.author = "" if not tl_data[0][2] else \
                tl_data[0][2].split('Author: ')[1] if 'Author: ' in tl_data[0][2] else ''
            self.transcriber = "" if not tl_data[1][2] else \
                tl_data[1][2].split('by ')[1] if 'by ' in tl_data[1][2] else ''
            self.style = "Simple"
            self.ev = tl_data[0][6]
            self.st_dev = tl_data[1][6]
            self.units = []
            for i in range(5):
                unit = Unit(tl_data[self.SIMPLE_UNIT_NAME_ROW][i + 2],
                            tl_data[self.SIMPLE_UNIT_LEVEL_ROW][i + 2],
                            tl_data[self.SIMPLE_UNIT_RANK_ROW][i + 2],
                            tl_data[self.SIMPLE_UNIT_STAR_ROW][i + 2],
                            tl_data[self.SIMPLE_UNIT_UE_ROW][i + 2])
                self.units.append(unit)

            tl_time = [row[7] for row in tl_data]
            tl_action = [row[8] for row in tl_data]
            if tl_time[0] == "Time":
                tl_time = tl_time[1:]
            if tl_action[0] == "Action Description":
                tl_action = tl_action[1:]

            if not tl_time[0] and tl_action[0]:
                tl_time[0] = '1:30'

            self.tl_labels = ["Time", "Action Description"]
            self.tl_actions = list(zip(tl_time, tl_action))
            self.unit_column = False
            self.simple = True

        self.thumbnail_url = boss_image_urls[boss]
        self.starting_cell_tuple = tl_cell_tuple
        self.boss_name = boss_names[boss]

    def __str__(self):
        return "Author: " + self.author + \
               "\nTranscriber:  " + self.transcriber + \
               "\nEV: " + self.ev + \
               "\nST_DEV: " + self.st_dev + \
               "\nStyle: " + self.style + \
               "\nUnits: " + str(self.units) + \
               "\nLabels " + str(self.tl_labels) + \
               "\nActions: " + str(list(self.tl_actions))


class Unit:
    def __init__(self, name, level, rank, star, ue):
        self.name = name
        self.level = level
        self.rank = rank
        self.star = star
        self.ue = ue

    def __str__(self):
        unit_string = f'{self.name}/LV{self.level}/R{self.rank}/{self.star}⭐/UE:{self.ue}\n'
        return unit_string


def load_to_db(boss, clear=False):
    timelines = SqliteDict(sqlitedict_base_path + str(boss) + '.sqlite', autocommit=True)
    if clear:
        timelines.clear()
    wk_sht = sheets_helper.get_timelines_worksheet(boss)
    tl_start = wk_sht.find('Original Author: [^_]', searchByRegex=True)
    tl_end = wk_sht.find('Extra Notes')
    zipped_timelines = zip(tl_start, tl_end)
    for tl in zipped_timelines:
        tl_cell_tuple = (tl[0].row, tl[0].col - 2)
        tl_data = wk_sht.get_values((tl[0].row, tl[0].col - 1), (tl[1].row + 3, tl[1].col + 7))
        timelines[tl_data[0][0]] = Timeline(tl_data, boss, tl_cell_tuple, False)
        print(tl_data)

    base_search_column = 4  # This is for boss 1, each boss afterwards is +10
    simple_wk_sht = sheets_helper.get_simple_timelines_worksheet(boss)
    tl_start = simple_wk_sht.find('Author: [^_]',
                                  cols=(base_search_column + (boss - 1) * 10, base_search_column + (boss - 1) * 10),
                                  searchByRegex=True)
    for tl in tl_start:
        tl_cell_tuple = (tl.row, tl.col - 2)
        tl_end_cell_tuple = (tl.row + 9, tl.col + 6)
        tl_data = simple_wk_sht.get_values(tl_cell_tuple, tl_end_cell_tuple)
        timelines[tl_data[0][0]] = Timeline(tl_data, boss, tl_cell_tuple, True)
        print(tl_data)


def load_to_db_thread(boss):
    while load_to_db_lock.locked():
        print(f"Loading is locked, trying again later for boss {boss}")
        time.sleep(30)  # Sleep for 30 seconds if locked

    load_to_db_lock.acquire(timeout=120)
    print(f"Loading for boss {boss}")
    load_to_db(boss)
    load_to_db_lock.release()
    threading.Timer(1800, load_to_db_thread, [boss]).start()


def background_load_to_db():
    RUNTIME_BUFFER = 30
    RUNTIME_DELAY = 360
    load_to_db_thread(1)
    time.sleep(RUNTIME_DELAY + RUNTIME_BUFFER)
    load_to_db_thread(2)
    time.sleep(RUNTIME_DELAY + RUNTIME_BUFFER)
    load_to_db_thread(3)
    time.sleep(RUNTIME_DELAY + RUNTIME_BUFFER)
    load_to_db_thread(4)
    time.sleep(RUNTIME_DELAY + RUNTIME_BUFFER)
    load_to_db_thread(5)

def get_from_db(boss, id):
    timelines = get_single_boss_timelines_from_db(boss)
    if id not in timelines:
        return None
    return timelines[id]


def get_single_boss_timelines_from_db(boss):
    return SqliteDict(sqlitedict_base_path + str(boss) + '.sqlite', autocommit=True)
