import pygsheets

# Auth things with gsheets
path = 'service_account.json'
gc = pygsheets.authorize(service_account_file=path)
translation_sheet_id = '11B6-6mmQC4XMTiSadrfKGlS_y4qSnLzfFHj1_W8XLhI'


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
    timelines_data_store = gc.open('Timelines data store')
    return timelines_data_store.worksheet(property='title', value='D' + str(boss))
