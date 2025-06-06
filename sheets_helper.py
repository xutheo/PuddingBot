import pygsheets
from clan_battle_info import (translation_sheet_id, get_sheet_id, test_sheet_id, dtier_sheet_ids,
                              dtier_simple_sheet_id, dtier_ots_id, get_homework_sheet_id,
                              homework_sheet_gid, roster_sheet_id, bosses_info_id, chorry_roster_sheet_id, borry_roster_sheet_id,
                              metrics_sheet_id, metrics_gid, metrics_test_gid)
from icon_bank import clean_text
import os

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
        if row[4].strip():
            mapping[clean_text(row[4])] = row[5].strip().split(";;;")
            skills_raw.append(row[5].strip())
    #print(mapping)
    return mapping
get_animation_videos()

def get_animation_videos_names_bank():
    # Get animation cancel videos
    main_sheet = gc.open_by_key(translation_sheet_id)
    animation_bank = main_sheet.worksheet(property='id', value=282243922)  # input
    mapping = {}
    names_bank = [name for name in animation_bank.get_col(5) if name]
    names_bank_cleaned = {}
    for name in names_bank:
        names_bank_cleaned[clean_text(name)] = name
    return names_bank_cleaned


def get_timelines_worksheet(boss):
    # Get the sheet that stores TLs
    sheet_id = get_sheet_id()
    timelines_data_store = gc.open_by_key(sheet_id)
    #timelines_data_store = gc.open_by_key(test_sheet_id)
    return timelines_data_store.worksheet(property='id', value=dtier_sheet_ids[boss])

def get_simple_timelines_worksheet(boss):
    # Get the sheet that stores TLs
    sheet_id = get_sheet_id()
    timelines_data_store = gc.open_by_key(sheet_id)
    #timelines_data_store = gc.open_by_key(test_sheet_id)
    return timelines_data_store.worksheet(property='id', value=dtier_simple_sheet_id)


def get_ots_worksheet(boss):
    # Get the sheet that stores TLs
    sheet_id = get_sheet_id()
    timelines_data_store = gc.open_by_key(sheet_id)
    #timelines_data_store = gc.open_by_key(test_sheet_id)
    return timelines_data_store.worksheet(property='id', value=dtier_ots_id)


def get_homework_worksheet_users(clan='Worry'):
    homework_sheet_id = get_homework_sheet_id(clan)
    sheets = gc.open_by_key(homework_sheet_id)
    sheets_wksht = sheets.worksheet(property='title', value='Welcome & Member Config')
    return sheets_wksht


def get_homework_worksheet(clan='Worry'):
    homework_sheet_id = get_homework_sheet_id(clan)
    # Get the sheet that stores TLs
    #if chorry:
    #    sheets = gc.open_by_key(chorry_homework_sheet_id)
    #    return sheets.worksheet(property='id', value=homework_sheet_gid)

    sheets = gc.open_by_key(homework_sheet_id)
    return sheets.worksheet(property='id', value=homework_sheet_gid)


def get_roster_worksheet_users(clan='Worry'):
    sheets = gc.open_by_key(roster_sheet_id if clan == 'Worry' else chorry_roster_sheet_id if clan == 'Chorry' else borry_roster_sheet_id)
    sheets_wksht = sheets.worksheet(property='title', value='Member Config')
    return sheets_wksht


def get_roster_worksheet(user):
    sheets_wksht = None
    not_special_users = user.lower() != 'sariel' and user.lower() != 'avatar' and user.lower() != 'ark'
    try:
        sheets = gc.open_by_key(roster_sheet_id if not_special_users else chorry_roster_sheet_id)
        sheets_wksht = sheets.worksheet(property='title', value=user)
    except:
        try:
            sheets = gc.open_by_key(chorry_roster_sheet_id if not_special_users else roster_sheet_id)
            sheets_wksht = sheets.worksheet(property='title', value=user)
        except:
            print("Could not find user in either roster sheet")
    return sheets_wksht


def get_roster_worksheet_by_idx(idx, chorry=False):
    sheets_wksht = None
    if not chorry:
        sheets = gc.open_by_key(roster_sheet_id)
        sheets_wksht = sheets.worksheet(property='index', value=idx)
        if sheets_wksht.title.lower() == 'sariel' or sheets_wksht.title.lower() == 'avatar' or sheets_wksht.title.lower() == 'ark':
            return None
    else:
        sheets = gc.open_by_key(chorry_roster_sheet_id)
        sheets_wksht = sheets.worksheet(property='index', value=idx)
    return sheets_wksht


def get_metrics_worksheet():
    if os.environ['COMPUTERNAME'] == 'ZALTEO' or os.environ['COMPUTERNAME'] == 'LAPTOP-RVEEJPKP':
        sheets = gc.open_by_key(metrics_sheet_id)
        sheets_wksht = sheets.worksheet(property='id', value=metrics_test_gid)
        return sheets_wksht

    sheets = gc.open_by_key(metrics_sheet_id)
    sheets_wksht = sheets.worksheet(property='id', value=metrics_gid)
    return sheets_wksht


def get_bosses_info():
    sheet_id = get_sheet_id()
    timelines_data_store = gc.open_by_key(sheet_id)
    bosses_info = timelines_data_store.worksheet(property='id', value=bosses_info_id).get_all_values()
    bosses_info_dict = {
        1: (bosses_info[2][3], f'https://redive.estertion.win/icon/unit/{bosses_info[4][2]}.webp'),
        2: (bosses_info[2][10], f'https://redive.estertion.win/icon/unit/{bosses_info[4][9]}.webp'),
        3: (bosses_info[2][17], f'https://redive.estertion.win/icon/unit/{bosses_info[4][16]}.webp'),
        4: (bosses_info[2][24], f'https://redive.estertion.win/icon/unit/{bosses_info[4][23]}.webp'),
        5: (bosses_info[2][31], f'https://redive.estertion.win/icon/unit/{bosses_info[4][30]}.webp')
    }
    print(bosses_info_dict)
    return bosses_info_dict
