from sheets_helper import get_homework_worksheet_users, get_roster_worksheet_users
from sqlitedict import SqliteDict
from icon_bank import icon_bank
from clan_battle_info import find_current_day, sqlitedict_base_path
import json
import datetime
import requests

class User:
    def __init__(self, display_name, discord_id, priconne_id):
        self.display_name = display_name
        self.discord_id = discord_id
        self.priconne_id = priconne_id
        self.roster_name = ''
        self.homework_name = ''

    def __str__(self):
        return (f'{self.display_name} - DiscordID: {self.discord_id},  PriconneID: {self.priconne_id} '
                f'RosterName: {self.roster_name}, HWName: {self.homework_name}')


worry_base_users = {}

chorry_base_users = {}

borry_base_users = {}

extra_users = {}

worry_discord_ids = {}
chorry_discord_ids = {}
borry_discord_ids = {}

null_discord_ids = {}
extra_discord_ids = SqliteDict(sqlitedict_base_path + 'extra_discord_ids.sqlite', autocommit=True)

def associate_discord_id(clan, priconne_id, discord_id):
    global worry_discord_ids
    global chorry_discord_ids
    global borry_discord_ids
    added = False
    if clan == 'Worry':
        worry_discord_ids[priconne_id] = discord_id
        added = True
    elif clan == 'Chorry':
        chorry_discord_ids[priconne_id] = discord_id
        added = True
    elif clan == 'Borry':
        borry_discord_ids[priconne_id] = discord_id
        added = True
    if added:
        extra_discord_ids[priconne_id] = discord_id

    if priconne_id in null_discord_ids:
        del null_discord_ids[priconne_id]


def remove_extra_discord_id(priconne_id):
    if priconne_id in extra_discord_ids:
        del extra_discord_ids[priconne_id]


def get_discord_ids():
    worry_url = 'https://roboninon.win/api/v1/priconne/clan/490028/members'
    chorry_url = 'https://roboninon.win/api/v1/priconne/clan/490549/members'
    borry_url = 'https://roboninon.win/api/v1/priconne/clan/489437/members'
    with open("ninon_api_keys.json") as api_keys:
        keys = json.load(api_keys)
        worry_key = keys['worry_key']
        chorry_key = keys['chorry_key']
        borry_key = keys['borry_key']

        worry_ninon_users = requests.get(worry_url, params={"key": worry_key})
        chorry_ninon_users = requests.get(chorry_url, params={"key": chorry_key})
        borry_ninon_users = requests.get(borry_url, params={"key": borry_key})

        if worry_ninon_users.ok:
            content = worry_ninon_users.json()
            for c in content:
                if c['discord_id']:
                    try:
                        # Olegase exception
                        if c['viewer_id'] and c['viewer_id'] == 445791452:
                            worry_discord_ids[445791452] = 102530746287149056
                            continue
                        worry_discord_ids[c['viewer_id']] = int(c['discord_id'])
                    except Exception as e:
                        print(f"Could not save worry discord id because of {e}")
                else:
                    if c['viewer_id'] and c['viewer_id'] in extra_discord_ids:
                        worry_discord_ids[c['viewer_id']] = extra_discord_ids[c['viewer_id']]
                    else:
                        null_discord_ids[c['viewer_id']] = c
        for id in worry_base_users:
            if id not in worry_discord_ids:
                worry_discord_ids[id] = worry_base_users[id].discord_id

        if chorry_ninon_users.ok:
            content = chorry_ninon_users.json()
            for c in content:
                # GarretK exception
                if c['viewer_id'] == 208175965:
                    chorry_discord_ids[208175965] = 225174985277177856
                    continue
                if c['discord_id']:
                    try:
                        # Avatar? Algedi? account
                        if c['viewer_id'] and c['viewer_id'] == 963789593:
                            chorry_discord_ids[963789593] = 300752504050679820
                            continue
                        chorry_discord_ids[c['viewer_id']] = c['discord_id']
                    except Exception as e:
                        print(f"Could not save chorry discord id because of {e}")
                else:
                    if c['viewer_id'] and c['viewer_id'] in extra_discord_ids:
                        chorry_discord_ids[c['viewer_id']] = extra_discord_ids[c['viewer_id']]
                    else:
                        null_discord_ids[c['viewer_id']] = c

        for id in chorry_base_users:
            if id not in chorry_discord_ids:
                chorry_discord_ids[id] = chorry_base_users[id].discord_id

        if borry_ninon_users.ok:
            content = borry_ninon_users.json()
            for c in content:
                if c['discord_id']:
                    try:
                        borry_discord_ids[c['viewer_id']] = int(c['discord_id'])
                    except Exception as e:
                        print(f"Could not save worry discord id because of {e}")
                else:
                    if c['viewer_id'] and c['viewer_id'] in extra_discord_ids:
                        borry_discord_ids[c['viewer_id']] = extra_discord_ids[c['viewer_id']]
                    else:
                        null_discord_ids[c['viewer_id']] = c

        for id in borry_base_users:
            if id not in borry_discord_ids:
                borry_discord_ids[id] = borry_base_users[id].discord_id

get_discord_ids()

def get_roster_users(clan='Worry'):
    roster_users_sheet = get_roster_worksheet_users(clan)
    roster_sheet_users = roster_users_sheet.get_values((2, 3), (31, 4))
    roster_users = {}
    for user in roster_sheet_users:
        roster_users[int(user[1])] = user[0][:-1]
    return roster_users


def get_homework_users_dict(clan='Worry'):
    homework_users_sheet = get_homework_worksheet_users(clan)
    homework_sheet_users = homework_users_sheet.get_values((3, 3), (32, 8))
    homework_users = {}
    #print(homework_sheet_users)
    for user in homework_sheet_users:
        homework_users[int(user[5])] = user[1]
    return homework_users

def get_homework_users(clan='Worry'):
    homework_users_dict = get_homework_users_dict(clan)
    homework_users = {}
    for id in homework_users_dict:
        homework_users[id] = User(display_name=homework_users_dict[id], discord_id=None, priconne_id=id)
    return homework_users

def generate_master_user_dict(clan='Worry'):
    homework_users = get_homework_users_dict(clan)
    roster_users = get_roster_users(clan) if clan=='Worry' or clan=='Chorry' else {}
    base_dict = worry_base_users if clan == 'Worry' else chorry_base_users if clan == 'Chorry' else borry_base_users
    master_users_dict = {}
    for id in base_dict:
        user = base_dict[id]
        aliases = set()
        aliases.add(user.display_name.lower())
        if id in homework_users:
            user.homework_name = homework_users[id]
            aliases.add(homework_users[id].lower())
        if id in roster_users:
            user.roster_name = roster_users[id]
            aliases.add(roster_users[id].lower())
        for alias in aliases:
            master_users_dict[alias] = user
    for id in homework_users:
        name = homework_users[id]
        if name.lower() not in master_users_dict:
            discord_id = None
            if id in worry_discord_ids:
                discord_id = worry_discord_ids[id]
            elif id in chorry_discord_ids:
                discord_id = chorry_discord_ids[id]
            elif id in borry_discord_ids:
                discord_id = borry_discord_ids[id]
            new_user = User(name, discord_id, id)
            new_user.homework_name = name
            master_users_dict[name.lower()] = new_user
            if id not in base_dict:
                extra_users[id] = new_user
    for id in roster_users:
        name = roster_users[id]
        if name.lower() not in master_users_dict:
            discord_id = None
            if id in worry_discord_ids:
                discord_id = worry_discord_ids[id]
            elif id in chorry_discord_ids:
                discord_id = chorry_discord_ids[id]
            elif id in borry_discord_ids:
                discord_id = borry_discord_ids[id]
            new_user = User(name, discord_id, id)
            new_user.roster_name = name
            master_users_dict[name.lower()] = new_user
            if id not in base_dict:
                extra_users[id] = new_user
    return master_users_dict


worry_users = generate_master_user_dict(clan='Worry')
#for user in worry_users:
#    print(f'{user}: {worry_users[user]}')
chorry_users = generate_master_user_dict(clan='Chorry')
borry_users = generate_master_user_dict(clan='Borry')

def regenerate_master_dict(clan):
    global worry_users
    global chorry_users
    global borry_users
    if clan == 'Worry':
        worry_users = generate_master_user_dict(clan='Worry')
    if clan == 'Chorry':
        worry_users = generate_master_user_dict(clan='Chorry')
    if clan == 'Borry':
        worry_users = generate_master_user_dict(clan='Borry')

'''for user in worry_users:
    print(user)
    print(worry_users[user])

for user in chorry_users:
    print(user)
    print(chorry_users[user])'''

def get_clan_dict(user):
    if not user:
        return None
    user_dict = None
    if user.lower() in worry_users:
        user_dict = worry_users
    elif user.lower() in chorry_users:
        user_dict = chorry_users
    elif user.lower() in borry_users:
        user_dict = borry_users
    else:
        return -1
    return user_dict


def find_user(user):
    if not user:
        return -1
    if user.lower() in worry_users:
        return worry_users[user.lower()]
    if user.lower() in chorry_users:
        return chorry_users[user.lower()]
    if user.lower() in borry_users:
        return borry_users[user.lower()]
    return -1


def find_user_by_id(id):
    if not id:
        return -1
    if id in worry_base_users:
        return worry_base_users[id]
    if id in chorry_base_users:
        return chorry_base_users[id]
    if id in extra_users:
        return extra_users[id]
    return -1

def find_user_by_discord_id(id):
    if not id:
        return None
    for name in worry_users:
        user = worry_users[name]
        if user.discord_id == id:
            return user
    for name in chorry_users:
        user = chorry_users[name]
        if user.discord_id == id:
            return user
    for name in borry_users:
        user = borry_users[name]
        if user.discord_id == id:
            return user
    return None

def find_clan_by_discord_id(id):
    if not id:
        return 'Worry'
    for viewer_id in worry_discord_ids:
        discord_id = worry_discord_ids[viewer_id]
        if id == discord_id:
            return 'Worry'
    for viewer_id in chorry_discord_ids:
        discord_id = chorry_discord_ids[viewer_id]
        if id == discord_id:
            return 'Chorry'
    for viewer_id in borry_discord_ids:
        discord_id = borry_discord_ids[viewer_id]
        if id == discord_id:
            return 'Borry'
    return 'Worry'


def find_discord_id_by_priconne_id(id):
    if not id:
        return None
    if id in worry_discord_ids:
        return worry_discord_ids[id]
    if id in chorry_discord_ids:
        return chorry_discord_ids[id]
    if id in borry_discord_ids:
        return borry_discord_ids[id]
    return None


def reset_fc_dicts():
    fc_status = SqliteDict(sqlitedict_base_path + 'fc.sqlite', autocommit=True)
    fc_status.clear()
    current_day = find_current_day()
    worry_hw_users = get_homework_users(clan='Worry')
    chorry_hw_users = get_homework_users(clan='Chorry')
    borry_hw_users = get_homework_users(clan='Borry')
    for id in worry_hw_users:
        fc_status[id] = (True, current_day)
    for id in chorry_hw_users:
        fc_status[id] = (True, current_day)
    for id in borry_hw_users:
        fc_status[id] = (True, current_day)

def mark_fc(id):
    fc_status = SqliteDict(sqlitedict_base_path + 'fc.sqlite', autocommit=True)
    current_day = find_current_day()
    if fc_status[id][1] != current_day:
        fc_status[id] = (False, current_day)
    else:
        fc_status[id] = (not fc_status[id][0], current_day)
    return fc_status[id]


def get_fc_status(clan='Worry'):
    fc_status = SqliteDict(sqlitedict_base_path + 'fc.sqlite', autocommit=True)

    count = 0
    first_half_string = ''
    second_half_string = ''
    base_dict = get_homework_users(clan)
    for id in base_dict:
        current_day = find_current_day()
        if fc_status[id][1] != current_day:
            fc_status[id] = (True, current_day)
        status = icon_bank['checkmark'] if fc_status[id][0] else icon_bank['redx']
        if count < 15:
            first_half_string += f'{base_dict[id].display_name}: {status}\n'
        else:
            second_half_string += f'{base_dict[id].display_name}: {status}\n'
        count += 1
    return (first_half_string, second_half_string)

'''
    Return codes:
        -1 = Cannot find target user
        -2 = Someone is already piloting the user
'''
def atc_start(discord_id, target_user):
    if not target_user:
        return -1
    atc_status = SqliteDict(sqlitedict_base_path + 'atc.sqlite', autocommit=True)
    user = find_user(target_user)
    if user == -1:
        return -1
    if user.priconne_id in atc_status:
        return -2
    atc_status[user.priconne_id] = (discord_id, datetime.datetime.now())
    if user.discord_id:
        return user.discord_id
    else:
        return user.display_name


'''
    Return codes:
        -1 = Cannot find target user
        -2 = Someone other than the pilot is trying to end
'''
def atc_end(discord_id, target_user, crash=False):
    if not target_user:
        return -1
    atc_status = SqliteDict(sqlitedict_base_path + 'atc.sqlite', autocommit=True)
    user = find_user(target_user)
    if user == -1:
        return -1
    priconne_id = user.priconne_id
    if priconne_id not in atc_status:
        return -1

    if not crash:
        pilot_discord_id = atc_status[priconne_id][0]
        if discord_id != pilot_discord_id:
            return -2
    del atc_status[priconne_id]
    if user.discord_id:
        return user.discord_id
    else:
        return user.display_name


def atc_status():
    status = SqliteDict(sqlitedict_base_path + 'atc.sqlite', autocommit=True)
    statuses = {}
    now = datetime.datetime.now()
    for id in status:
        user = find_user_by_id(int(id))
        discord_id, timestamp = status[id]
        timedelta = now - timestamp
        seconds = timedelta.seconds
        if seconds // 3600 > 0:
            time_string = '{:02}h, {:02}m, {:02}s'.format(seconds // 3600, seconds % 3600 // 60, seconds % 60)
        else:
            time_string = '{:02}m, {:02}s'.format(seconds % 3600 // 60, seconds % 60)
        if discord_id not in statuses:
            statuses[discord_id] = [(user.display_name, time_string)]
        else:
            statuses[discord_id].append((user.display_name, time_string))
    return statuses


def reset_atc_dict():
    atc_status = SqliteDict(sqlitedict_base_path + 'atc.sqlite', autocommit=True)
    atc_status.clear()

#print(atc_status())
'''#reset_atc_dict()
print(atc_start(152242204826533889, 'dabomstew'))
print(atc_start(152242204826533889, 'woody'))
atc_statuss = SqliteDict(sqlitedict_base_path + 'atc.sqlite', autocommit=True)
for status in atc_statuss:
    print(status, atc_statuss[status])
print(atc_status())'''

'''reset_fc_dicts()
fc_status = SqliteDict(sqlitedict_base_path + 'fc.sqlite', autocommit=True)
for x in fc_status:
    print(x, fc_status[x])
get_fc_status(True)'''