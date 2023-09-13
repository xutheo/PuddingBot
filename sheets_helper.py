import pygsheets

# Auth things with gsheets
path = 'service_account.json'
gc = pygsheets.authorize(service_account_file=path)
translation_sheet_id = '11B6-6mmQC4XMTiSadrfKGlS_y4qSnLzfFHj1_W8XLhI'
boss_urls = {
    1: "https://redive.estertion.win/icon/unit/302103.webp",
    2: "https://redive.estertion.win/icon/unit/302000.webp",
    3: "https://redive.estertion.win/icon/unit/300703.webp",
    4: "https://redive.estertion.win/icon/unit/302903.webp",
    5: "https://redive.estertion.win/icon/unit/301403.webp"
}

sheet_ids = {
    1: "1344830706",
    2: "1148100815",
    3: "337535649",
    4: "1030273266",
    5: "311078222"
}
def get_translation_mapping():
    # Get the translation mapping
    translation_sheet = gc.open_by_key(translation_sheet_id)
    translation_bank = translation_sheet.worksheet(property='id', value=0)  # input
    mapping = []
    all_values = translation_bank.get_all_values()
    for idx, row in enumerate(all_values):
        if row[2].strip() and row[3].strip() and (not row[2].startswith("CN/JP") or not row[3].startswith("EN")):
            mapping.append([row[2].strip(), row[3].strip()])

    mapping.sort(key=lambda x: len(x[0]), reverse=True)
    return mapping


def get_timelines_worksheet(boss):
    # Get the sheet that stores TLs
    timelines_data_store = gc.open('Copy of WorryChefs CB66 (08/23)')
    return timelines_data_store.worksheet(property='title', value='D' + str(boss) + ' Manual')


class Timelines:
    timelines = {}

    def __init__(self, boss):
        self.boss = boss
        wk_sht = get_timelines_worksheet(boss)
        tl_start = wk_sht.find('Original Author: [^_]', searchByRegex=True)
        tl_end = wk_sht.find('Extra Notes')
        timelines = zip(tl_start, tl_end)
        for tl in timelines:
            tl_cell_tuple = (tl[0].row, tl[0].col - 2)
            tl_data = wk_sht.get_values((tl[0].row, tl[0].col - 1), (tl[1].row + 3, tl[1].col + 7))
            self.timelines[tl_data[0][0]] = Timeline(tl_data, boss, tl_cell_tuple)
            print(tl_data)


class Timeline:
    UNIT_NAME_ROW = 2
    UNIT_LEVEL_ROW = 7
    UNIT_RANK_ROW = 8
    UNIT_STAR_ROW = 9
    UNIT_UE_ROW = 10

    TL_START_ROW = 15
    TL_COL_LABELS_ROW = 13
    TL_STARTING_SET_ROW = 14

    unit_column = False
    units = []

    def __init__(self, tl_data, boss, tl_cell_tuple):
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
            self.units.append(Unit(tl_data[self.UNIT_NAME_ROW][i + 1],
                                   tl_data[self.UNIT_LEVEL_ROW][i + 1],
                                   tl_data[self.UNIT_RANK_ROW][i + 1],
                                   tl_data[self.UNIT_STAR_ROW][i + 1],
                                   tl_data[self.UNIT_UE_ROW][i + 1]))
        tl_end_row = len(tl_data)
        self.tl_labels = list(filter(None, tl_data[self.TL_COL_LABELS_ROW]))
        if self.tl_labels[1] == 'Unit':
            self.unit_column = True
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
