from sqlitedict import SqliteDict
import sheets_helper
from sheets_helper import sheet_ids
from sheets_helper import boss_urls
import os
sqlitedict_base_path = f"/mnt/timeline_data/test_"
if os.environ['COMPUTERNAME'] == 'ZALTEO':
    sqlitedict_base_path = f"./mnt/timeline_data/test_"


def load_to_db(boss):
    timelines = SqliteDict(sqlitedict_base_path + str(boss) + '.sqlite', autocommit=True)
    wk_sht = sheets_helper.get_timelines_worksheet(boss)
    tl_start = wk_sht.find('Original Author: [^_]', searchByRegex=True)
    tl_end = wk_sht.find('Extra Notes')
    zipped_timelines = zip(tl_start, tl_end)
    for tl in zipped_timelines:
        tl_cell_tuple = (tl[0].row, tl[0].col - 2)
        tl_data = wk_sht.get_values((tl[0].row, tl[0].col - 1), (tl[1].row + 3, tl[1].col + 7))
        timelines[tl_data[0][0]] = Timeline(tl_data, boss, tl_cell_tuple)
        print(tl_data)


def get_from_db(boss, id):
    timelines = get_single_boss_timelines_from_db(boss)
    if id not in timelines:
        return None
    return timelines[id]


def get_single_boss_timelines_from_db(boss):
    return SqliteDict(sqlitedict_base_path + str(boss) + '.sqlite', autocommit=True)


class Timeline:
    UNIT_NAME_ROW = 2
    UNIT_LEVEL_ROW = 7
    UNIT_RANK_ROW = 8
    UNIT_STAR_ROW = 9
    UNIT_UE_ROW = 10

    TL_START_ROW = 15
    TL_COL_LABELS_ROW = 13
    TL_STARTING_SET_ROW = 14

    def __init__(self, tl_data, boss, tl_cell_tuple):
        self.units = []
        self.id = tl_data[0][0]
        self.sheet_id = sheet_ids[boss]
        self.starting_cell_tuple = tl_cell_tuple
        self.thumbnail_url = boss_urls[boss]
        self.author = "" if not tl_data[0][1] else tl_data[0][1].split('Original Author: ')[1]
        print(self.author)
        print(tl_data)
        self.transcriber = "" if not tl_data[1][1] else tl_data[1][1].split('by ')[1]
        self.ev = tl_data[1][7]
        self.st_dev = tl_data[2][7]
        self.style = tl_data[4][0]
        self.status = tl_data[6][0]
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
        self.tl_actions = tl_data[self.TL_START_ROW:tl_end_row-2]
        labels_length = len(self.tl_labels)
        actions_length = len(self.tl_actions[0])
        for tl_action in self.tl_actions:
            del tl_action[labels_length - 2: actions_length - 2]


    def __str__(self):
        return "Author: " + self.author +\
               "\nTranscriber:  " + self.transcriber +\
               "\nEV: " + self.ev +\
               "\nST_DEV: " + self.st_dev +\
               "\nStyle: " + self.style +\
               "\nStatus: " + self.status +\
               "\nUnits: " + str(self.units) +\
               "\nLabels " + str(self.tl_labels) +\
               "\nStarting Set Status: " + str(self.starting_set_status) +\
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