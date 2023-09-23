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

def get_animation_videos(raw):
    # Get animation cancel videos
    main_sheet = gc.open_by_key(translation_sheet_id)
    animation_bank = main_sheet.worksheet(property='index', value=1)  # input
    mapping = []
    skills_raw = []
    all_values = animation_bank.get_all_values()
    _=0
    if not raw: _ = 2

    for idx, row in enumerate(all_values):
        if row[2+_].strip() and row[3+_].strip():
            mapping.append([row[2+_].strip(), row[3+_].strip().split(" ------------------------------------- ")])
            skills_raw.append(row[3+_].strip())

    for i in range(len(mapping)):
        for j in range(len(mapping[i][1])):
            mapping[i][1][j] = mapping[i][1][j].strip()

    if raw:
        return mapping, skills_raw
    else:
        return mapping

def translate_animation_videos():
    # Translates all japanese characters to english from the animation cancelling videos if relevant translation is available (run the command from this file)
    main_sheet = gc.open_by_key(translation_sheet_id)
    translated_bank = main_sheet.worksheet(property='index', value=1)  # input
    animation_untranslated, skills_raw = get_animation_videos(True)
    translation_mapping = get_translation_mapping()
    skills_translation_bank = [["スキル", " Skill "], ["通常攻撃", " AA"], ["■", ""], ["\\u3000", " "], ["カウンター", "Counter"], ["トークン", "Summon"]]

    names_bank = ",".join([i[0] for i in animation_untranslated])
    skills_bank = ",".join(skills_raw)

    for i in translation_mapping: names_bank = names_bank.replace(i[0],i[1])
    for i in skills_translation_bank: skills_bank = skills_bank.replace(i[0],i[1])

    translated_bank.update_col(5, names_bank.split(","), 2)
    translated_bank.update_col(6, skills_bank.split(","), 2)

def get_timelines_worksheet(boss):
    # Get the sheet that stores TLs
    timelines_data_store = gc.open_by_key(sheet_id)
    #timelines_data_store = gc.open_by_key(test_sheet_id)
    return timelines_data_store.worksheet(property='id', value=dtier_sheet_ids[boss])
