from sqlitedict import SqliteDict
import sheets_helper
from clan_battle_info import dtier_sheet_ids, get_boss_names, get_boss_urls, dtier_simple_sheet_id, sqlitedict_base_path
import os
import threading
import time
from threading import Lock
import numpy as np
import pandas as pd

load_to_db_lock = Lock()

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

    def __init__(self, tl_data, boss, tl_cell_tuple, simple, ot=False):
        if not simple:
            while tl_data[self.TL_COL_LABELS_ROW][0] != 'Time':
                self.TL_COL_LABELS_ROW += 1
                self.TL_START_ROW += 1
                self.TL_STARTING_SET_ROW += 1
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
            # We need to delete extra columns because action description takes up more than one column
            cols_to_delete = []
            for i in range(labels_length-2, actions_length-2):
                cols_to_delete.append(i)
            self.tl_actions = np.delete(self.tl_actions, cols_to_delete, 1)
            #print(f"self tl actions: {self.tl_actions}")
            #for tl_action in self.tl_actions:
            #    del tl_action[labels_length - 2: actions_length - 2]
            self.simple = False
        else:
            self.id = tl_data[0][0]
            self.sheet_id = dtier_simple_sheet_id
            self.author = "" if not tl_data[0][2] else \
                tl_data[0][2].split('Author: ')[1] if 'Author: ' in tl_data[0][2] else ''
            self.transcriber = "" if not tl_data[1][2] else \
                tl_data[1][2].split('by ')[1] if 'by ' in tl_data[1][2] else ''
            self.style = "Simple" if not ot else "OT"
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

        self.thumbnail_url = get_boss_urls()[boss-1]
        self.starting_cell_tuple = tl_cell_tuple
        self.boss_name = get_boss_names()[boss-1]

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

    ''' Grabs the Manual TL worksheet and stores manual tls in pudding bot '''
    wk_sht = sheets_helper.get_timelines_worksheet(boss)
    all_complex_tls = np.array(wk_sht.get_all_values(), dtype='object')
    df = pd.DataFrame(all_complex_tls)
    find_author = df.apply(lambda col: col.str.contains('Original Author: [^_]', na=False), axis=1)
    find_notes = df.apply(lambda col: col.str.contains('Extra Notes', na=False), axis=1)

    tl_start = []
    for index, row in find_author.iterrows():
        for i in range(len(row)):
            if row[i]:
                tl_start.append((index + 1, i + 1))

    tl_end = []
    for index, row in find_notes.iterrows():
        for i in range(len(row)):
            if row[i]:
                tl_end.append((index + 1, i + 1))

    tl_end_idx = 0
    zipped_timelines = []
    for start in tl_start:
        while tl_end[tl_end_idx][0] < start[0]:
            tl_end_idx += 1
        zipped_timelines.append((start, tl_end[tl_end_idx]))

    for tl in zipped_timelines:
        tl_cell_tuple = (tl[0][0], tl[0][1] - 2)
        tl_data2 = all_complex_tls[tl[0][0]-1:tl[1][0]+1, tl[0][1] - 2:tl[1][1] + 7]
        timelines[tl_data2[0][0]] = Timeline(tl_data2, boss, tl_cell_tuple, False)
        time2_3 = time.time()

    ''' Grabs the Simple TL worksheet and stores simple tls in pudding bot '''
    base_search_column = 4  # This is for boss 1, each boss afterwards is +10
    simple_wk_sht = sheets_helper.get_simple_timelines_worksheet(boss)
    tl_start = []
    all_simple_tls = np.array(simple_wk_sht.get_all_values(), dtype='object')
    df = pd.DataFrame(all_simple_tls)
    find_author_simple = df.apply(lambda col: col.str.contains('Author: [^_]', na=False), axis=1)
    search_column = base_search_column + (boss - 1) * 10 - 1
    for index, row in find_author_simple.iterrows():
        if row[search_column]:
            tl_start.append((index + 1, search_column + 1))

    for tl in tl_start:
        tl_cell_tuple = (tl[0], tl[1] - 2)
        tl_end_cell_tuple = (tl[0] + 9, tl[1] + 6)
        #tl_data = simple_wk_sht.get_values(tl_cell_tuple, tl_end_cell_tuple)
        tl_data2 = all_simple_tls[tl[0] - 1:tl[0] + 9, tl[1] - 3: tl[1] + 6]
        timelines[tl_data2[0][0]] = Timeline(tl_data2, boss, tl_cell_tuple, True)
    time5 = time.time()
    #print(f'Zip and store simple tls: {time5-time4}')

    ''' Grabs the OT TL worksheet and stores OT tls in pudding bot '''
    ot_wk_sht = sheets_helper.get_ots_worksheet(boss)
    all_ot_tls = np.array(ot_wk_sht.get_all_values(), dtype='object')
    ot_tl_start = []
    df = pd.DataFrame(all_ot_tls)
    find_author_ot = df.apply(lambda col: col.str.contains('Author: [^_]', na=False), axis=1)
    search_column = base_search_column + (boss - 1) * 10 - 1
    for index, row in find_author_ot.iterrows():
        if row[search_column]:
            ot_tl_start.append((index + 1, search_column + 1))

    for ot_tl in ot_tl_start:
        tl_cell_tuple = (ot_tl[0], ot_tl[1] - 2)
        tl_end_cell_tuple = (ot_tl[0] + 9, ot_tl[1] + 6)
        tl_data2 = all_ot_tls[ot_tl[0] - 1:ot_tl[0] + 9, ot_tl[1] - 3: ot_tl[1] + 6]
        timelines[tl_data2[0][0]] = Timeline(tl_data2, boss, tl_cell_tuple, True, True)


def background_load_tl():
    while True:
        print('Background saving boss 1')
        load_to_db(1)
        time.sleep(120)
        print('Background saving boss 2')
        load_to_db(2)
        time.sleep(120)
        print('Background saving boss 3')
        load_to_db(3)
        time.sleep(120)
        print('Background saving boss 4')
        load_to_db(4)
        time.sleep(120)
        print('Background saving boss 5')
        load_to_db(5)
        time.sleep(120)


def get_from_db(boss, id):
    timelines = get_single_boss_timelines_from_db(boss)
    if id not in timelines:
        return None
    return timelines[id]


def get_single_boss_timelines_from_db(boss):
    return SqliteDict(sqlitedict_base_path + str(boss) + '.sqlite', autocommit=True)
