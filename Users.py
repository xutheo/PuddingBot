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


worry_base_users = {
    449396331: User('Astordor', 203168191889801217, 336253788),
    852701662: User('Dabomstew', 79515100536385536, 852701662),
    576099458: User('Woody', 416540817168007189, 576099458),
    725436445: User('Tomoeri', 426704723962232834, 725436445),
    631710942: User('Kami', 268457898001039362, 631710942),
    612311272: User('Arjen', 244555857994448906, 612311272),
    527270031: User('Hachimitsu', 852629725179674675, 527270031),
    448053269: User('Olegase', 201054689800880128, 448053269),
    640789706: User('Chocolate', 431497734047137812, 640789706),
    263503371: User('Squawk', 395509094934642688, 263503371),
    516973449: User('Panda', 218907301199872000, 516973449),
    865633484: User('Mimicon', 466488841201516545, 865633484),
    698454373: User('Reonidas', 327401833561587713, 698454373),
    573657443: User('Takamori', 484142867044892696, 573657443),
    221209908: User('Shuffling', 186493198007271424, 221209908),
    420434940: User('Kyruto', 460222637155549204, 420434940),
    313569259: User('Dragon', 305127967141658624, 313569259),
    865498980: User('Asandari', 126783165342679041, 865498980),
    913842239: User('Kana', 250690641149820938, 913842239),
    675911323: User('Justin', 141248381610754049, 675911323),
    324304754: User('Belial', 87386705010630656, 324304754),
    548338315: User('VVanky', 186148103877951488, 548338315),
    765932856: User('Richard', 297122012449734676, 765932856),
    924182772: User('Shiari', 710261281617084458, 924182772),
    136787075: User('Yuzu', 443785872807297024, 136787075),
    973891706: User('Pyragon', 215985215468732418, 973891706),
    903158276: User('Arxos', 182221373475782656, 903158276),
    477080470: User('Zalteo', 152242204826533889, 477080470),
}
# Manually add astordor, justin, richard

chorry_base_users = {
    911255036: User('Ark', 766868393848340480, 911255036),
    269768284: User('ViiPenguin', 192114683090698241, 269768284),
    117194181: User('Kirby', 143361945804734464, 117194181),
    826140928: User('Rin', 277026949178851329, 826140928),
    801922329: User('Avir', 791397594827587624, 801922329),
    293195590: User('LastTour', 956960841259954257, 293195590),
    788536578: User('Kou', 408955778456748042, 788536578),
    158447620: User('Kuron', 584402132778745887, 158447620),
    793505279: User('Sariel', 408470996773765120, 793505279),
    817101890: User('Osmium', 656489366616670228, 817101890),
    498111620: User('Momiji', 255197886059511808, 498111620),
    201127998: User('Algedi', 145513216187826176, 201127998),
    244327197: User('Ern＠2', 486164996645060618, 244327197),
    121242234: User('Mio', 372390056301690894, 121242234),
    778458742: User('Ecu', 200245308985180160, 778458742),
    715457115: User('Xern', 406664128997097482, 715457115),
    680795925: User('Noinloki', 581303630292975627, 680795925),
    344543240: User('NXH', 201830731012505601, 344543240),
    554628237: User('Fulano', 237988764012511234, 554628237),
    245884571: User('Woody2', 416540817168007189, 245884571),
    216755573: User('VIPfighter', 178138531758080000, 216755573),
    937918198: User('Rei', 163682455197319168, 937918198),
    177901622: User('Jaym', 88044613750759424, 177901622),
    324585111: User('Nata', 173202402567127040, 324585111),
    906356205: User('DarkGe', 408245460445167627, 906356205),
    484301869: User('Kut', 146283850245472256, 484301869),
    879936134: User('AtherialDovah', 186582097463345152, 879936134),
    963789593: User('Avatar', 218199797184724993, 963789593),
    131899805: User('Paris', 630909379113254922, 131899805),
}
# Manually add doremy, nxh, and sariel

borry_base_users = {}

extra_users = {}

worry_discord_ids = {}
chorry_discord_ids = {}
borry_discord_ids = {}

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
                        worry_discord_ids[c['viewer_id']] = int(c['discord_id'])
                    except Exception as e:
                        print(f"Could not save worry discord id because of {e}")

        for id in worry_base_users:
            if id not in worry_discord_ids:
                worry_discord_ids[id] = worry_base_users[id].discord_id

        if chorry_ninon_users.ok:
            content = chorry_ninon_users.json()
            for c in content:
                if c['discord_id']:
                    try:
                        chorry_discord_ids[c['viewer_id']] = c['discord_id']
                    except Exception as e:
                        print(f"Could not save chorry discord id because of {e}")

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