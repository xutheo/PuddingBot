import pygsheets
from clan_battle_info import translation_sheet_id, sheet_id, test_sheet_id, dtier_sheet_ids
import re

# Auth things with gsheets
path = 'service_account.json'
gc = pygsheets.authorize(service_account_file=path)


def get_translation_mapping():
    # Get the translation mapping
    translation_sheet = gc.open_by_key(translation_sheet_id)
    translation_bank = translation_sheet.worksheet(property='id', value=0)  # input
    mapping = []
    all_values = translation_bank.get_all_values()
    for idx, row in enumerate(all_values):
        if row[2].strip() and row[3].strip() and (not row[2].startswith("CN/JP") or not row[3].startswith("EN")):
            mapping.append([row[2].strip(), row[3].strip()])

    #skills_translation_bank = {"スキル": " Skill ", "通常攻撃": " AA", "■": "", "\\u3000": " ", "カウンター": "Counter", "トークン": "Summon"}
    mapping.sort(key=lambda x: len(x[0]), reverse=True)
    return mapping


def get_animation_videos():
    # Get animation cancel videos
    main_sheet = gc.open_by_key(translation_sheet_id)
    animation_bank = main_sheet.worksheet(property='id', value=282243922)  # input
    mapping = {}
    skills_raw = []
    all_values = animation_bank.get_all_values()

    for idx, row in enumerate(all_values):
        if row[4].strip() and row[5].strip():
            mapping[row[4].strip().lower()] = row[5].strip().split(";;;")
            skills_raw.append(row[5].strip())

    return mapping
'''#クウカ
main_sheet = gc.open_by_key(translation_sheet_id)
animation_bank = main_sheet.worksheet(property='id', value=282243922)  # input
all_values = animation_bank.get_all_values()


for idx, row in enumerate(all_values):
    if idx < 160: continue
    print(idx, row)
    animation_bank.update_value((idx+1, 6), re.sub('-{5,}', ';;;', row[5]))'''



#bank = get_animation_videos()
#print(bank['labyrista'])

def get_timelines_worksheet(boss):
    # Get the sheet that stores TLs
    timelines_data_store = gc.open_by_key(sheet_id)
    #timelines_data_store = gc.open_by_key(test_sheet_id)
    return timelines_data_store.worksheet(property='id', value=dtier_sheet_ids[boss])
