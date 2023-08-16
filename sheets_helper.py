import pygsheets

# Auth things with gsheets
path = 'service_account.json'
gc = pygsheets.authorize(service_account_file=path)


def get_translation_mapping(sheet_name):
    # Get the translation mapping
    translation_sheet = gc.open(sheet_name)
    translation_bank = translation_sheet.worksheet(property='title', value='Sheet1')  # input
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
