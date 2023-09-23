import pygsheets
from clan_battle_info import translation_sheet_id, sheet_id, test_sheet_id, dtier_sheet_ids

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

    mapping.sort(key=lambda x: len(x[0]), reverse=True)
    return mapping


def get_timelines_worksheet(boss):
    # Get the sheet that stores TLs
    timelines_data_store = gc.open_by_key(sheet_id)
    #timelines_data_store = gc.open_by_key(test_sheet_id)
    return timelines_data_store.worksheet(property='id', value=dtier_sheet_ids[boss])

get_timelines_worksheet(1)