import pygsheets.exceptions
from sqlitedict import SqliteDict
import sheets_helper
from sheets_helper import get_homework_worksheet
from Timelines import get_single_boss_timelines_from_db, sqlitedict_base_path
from icon_bank import clean_text, shorten_name
from time import sleep
from Users import worry_users, chorry_users
import json
from clan_battle_info import score_multipliers

class Composition:
    def __init__(self, units, tl_code, ev, borrow=None):
        self.units = units
        self.tl_code = tl_code
        self.ev = ev
        self.borrow = borrow
        try:
            self.boss = int(self.tl_code[1])
        except:
            self.boss = None

    def __str__(self):
        return f'Units: {str(self.units)}\nTL Code: {self.tl_code}\nEV:{self.ev}\nBorrow:{self.borrow}\n'

    def evaluate_length(self):
        if len(list(filter(None, self.units))) < 4:
            return True
        return False

    def evaluate_ev(self):
        if self.ev:
            return False
        return True

    def evaluate_tl_code(self):
        if self.tl_code:
            return False
        return True

    def evaluate_borrow(self):
        if self.borrow:
            return False
        return True

    def compare(self, comp):
        for unit in self.units:
            if unit in comp.units:
                return unit

        return None

    def compare_count(self, comp):
        count = 0
        for unit in self.units:
            if unit in comp.units:
                count += 1

        return count


class Conflicts:
    def __init__(self):
        self.length_conflicts = []
        self.unit_conflicts = []
        self.ev_conflicts = []
        self.tl_code_conflicts = []
        self.borrow_conflicts = []


class Homework:
    COMP_ROW_OFFSET = 4
    COMP_COL_OFFSET = 5

    EV_ROW_OFFSET = 7
    EV_COL_OFFSET = 3
    TL_CODE_ROW_OFFSET = 5
    BORROW_COL_OFFSET = 10

    BETWEEN_COMPS_ROW_OFFSET = 6

    def __init__(self, user, homework_grid=None, roster_box=None, sheet=None):
        self.user = user
        self.roster_box = None
        if user.lower() in worry_users:
            self.id = worry_users[user.lower()].priconne_id
        elif user.lower() in chorry_users:
            self.id = chorry_users[user.lower()].priconne_id

        if homework_grid:
            comp1_units = []
            comp2_units = []
            comp3_units = []
            for i in range(self.COMP_COL_OFFSET, self.COMP_COL_OFFSET + 4):
                comp1_units.append(homework_grid[self.COMP_ROW_OFFSET][i])
                comp2_units.append(homework_grid[self.COMP_ROW_OFFSET + self.BETWEEN_COMPS_ROW_OFFSET][i])
                comp3_units.append(homework_grid[self.COMP_ROW_OFFSET + 2 * self.BETWEEN_COMPS_ROW_OFFSET][i])

            self.comp1 = Composition(comp1_units,
                                     homework_grid[self.TL_CODE_ROW_OFFSET][self.EV_COL_OFFSET],
                                     homework_grid[self.EV_ROW_OFFSET][self.EV_COL_OFFSET],
                                     homework_grid[self.COMP_ROW_OFFSET][self.BORROW_COL_OFFSET])

            self.comp2 = Composition(comp2_units,
                                     homework_grid[self.TL_CODE_ROW_OFFSET + self.BETWEEN_COMPS_ROW_OFFSET][self.EV_COL_OFFSET],
                                     homework_grid[self.EV_ROW_OFFSET + self.BETWEEN_COMPS_ROW_OFFSET][self.EV_COL_OFFSET],
                                     homework_grid[self.COMP_ROW_OFFSET + self.BETWEEN_COMPS_ROW_OFFSET][self.BORROW_COL_OFFSET])

            self.comp3 = Composition(comp3_units,
                                     homework_grid[self.TL_CODE_ROW_OFFSET + 2 * self.BETWEEN_COMPS_ROW_OFFSET][self.EV_COL_OFFSET],
                                     homework_grid[self.EV_ROW_OFFSET + 2 * self.BETWEEN_COMPS_ROW_OFFSET][self.EV_COL_OFFSET],
                                     homework_grid[self.COMP_ROW_OFFSET + 2 * self.BETWEEN_COMPS_ROW_OFFSET][self.BORROW_COL_OFFSET])
        else:
            if roster_box:
                self.roster_box = roster_box
            else:
                self.load_units_available(sheet)


    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


    '''
    Evaluates the homework provided by the user in the google sheet and checks if it a possible allocation
    '''
    def evaluate(self):
        conflicts = Conflicts()
        conflicts.length_conflicts = [self.comp1.evaluate_length(), self.comp2.evaluate_length(), self.comp3.evaluate_length()]

        unit_conflicts = []
        unit_conflicts.append(self.comp1.compare(self.comp2))
        unit_conflicts.append(self.comp2.compare(self.comp3))
        unit_conflicts.append(self.comp3.compare(self.comp1))
        conflicts.unit_conflicts = unit_conflicts

        conflicts.ev_conflicts = [self.comp1.evaluate_ev(), self.comp2.evaluate_ev(), self.comp3.evaluate_ev()]
        conflicts.tl_code_conflicts = [self.comp1.evaluate_tl_code(), self.comp2.evaluate_tl_code(), self.comp3.evaluate_tl_code()]
        conflicts.borrow_conflicts = [self.comp1.evaluate_borrow(), self.comp2.evaluate_borrow(), self.comp3.evaluate_borrow()]
        return conflicts


    '''
    Using the user's unit box, gives a recommendation on a 3 comp allocation with preference to a specific boss
    '''
    def get_possible_comps(self, no_manual=False):
        possible_comps = {}
        for i in range(1, 6):
            possible_comps[i] = {}
            timelines = get_single_boss_timelines_from_db(i)
            for id in timelines:
                tl = timelines[id]
                if tl.style == 'OT' or (no_manual and 'Manual' in tl.style):
                    continue
                if id in get_banned_tls():
                    continue
                unit_names = []
                owned_units = 0
                borrow_unit = None
                for unit in tl.units:
                    unit_name_cleaned = clean_text(unit.name)
                    unit_names.append(unit_name_cleaned)
                    if unit_name_cleaned in self.roster_box and self.roster_box[unit_name_cleaned]:
                        owned_units += 1
                    else:
                        borrow_unit = unit_name_cleaned

                # Include in possible comps only if user owns 4 or 5 of the units
                if owned_units == 5:
                    possible_comps[i][id] = Composition(unit_names, id, tl.ev, borrow_unit)
                elif owned_units == 4:
                    possible_comps[i][id] = Composition(unit_names, id, tl.ev, borrow_unit)

                '''for unit in tl.units:
                    if unit.name not in unit_counts:
                        unit_counts[unit.name] = 1
                    else:
                        unit_counts[unit.name] += 1'''
        return possible_comps

    def load_units_available(self, sheet):
        roster_start_tuple = (4, 2)
        roster_end_tuple = (500, 5)
        roster_worksheet = sheet

        if not sheet:
            roster_worksheet = sheets_helper.get_roster_worksheet(self.user)
            if not roster_worksheet:
                self.roster_box = None
                return

        self.roster_box = {}
        units_available = roster_worksheet.get_values(roster_start_tuple, roster_end_tuple)
        for unit in units_available:
            #print(unit)
            self.roster_box[shorten_name(clean_text(unit[0]))] = True if unit[2] == 'TRUE' else False
        #print(self.roster_box)

    '''
    Let n be the total comps and k be the number of units
    Total operations: O(n^3k^2)
    
    In practice however, k < n < 50 so brute force is valid
    Search space is max 50 comps total with 5 units each
    Divided by boss number, each boss will have 10 comps
    We loop 5C3 = 10 times assuming we don't allocate the same boss twice
    The evaluate_alloc function will run around 150 comparison operations.
    Therefore max operations possible is 10*10*10*10*150 = 1500000
    This is very low and in fact retrieving google sheets takes more time than this method.
    '''
    def get_all_possible_allocs(self, possible_comps, same_boss_alloc=False, tl_filters = None):
        allocs = []
        for boss1 in range(1, 6):
            for boss2 in range(1, 6):
                if same_boss_alloc and boss1 > boss2:
                    continue
                elif not same_boss_alloc and boss1 >= boss2:
                    continue
                for boss3 in range(1, 6):
                    if same_boss_alloc and boss2 > boss3:
                        continue
                    elif not same_boss_alloc and boss2 >= boss3:
                        continue
                    for comp1 in possible_comps[boss1]:
                        for comp2 in possible_comps[boss2]:
                            if int(comp1[1:]) >= int(comp2[1:]):
                                continue
                            for comp3 in possible_comps[boss3]:
                                if int(comp2[1:]) >= int(comp3[1:]):
                                    continue
                                satisfies_filter = True
                                if tl_filters:
                                    satisfies = False
                                    for tl_filter in tl_filters:
                                        if tl_filter and comp1 in tl_filter[1] and comp2 in tl_filter[1] and comp3 in tl_filter[1]:
                                            satisfies = True
                                    satisfies_filter = satisfies
                                if satisfies_filter:
                                    alloc = [possible_comps[boss1][comp1], possible_comps[boss2][comp2], possible_comps[boss3][comp3]]
                                    if self.evaluate_alloc(alloc):
                                        total_ev = 0
                                        ids = ','.join([comp.tl_code for comp in alloc])
                                        for comp in alloc:
                                            total_ev += convert_ev_to_float(comp.ev)
                                        allocs.append((ids, alloc, total_ev))
        return allocs


    def get_recommended_allocs(self, no_manual=False, boss_preference=None, same_boss_alloc=False):
        #start = time.time()
        possible_comps = self.get_possible_comps(no_manual)
        #get_possible_comps_time = time.time()
        #print(get_possible_comps_time - start)
        allocs = self.get_all_possible_allocs(possible_comps, same_boss_alloc)
        #get_all_possible_allocs_time = time.time()
        #print(get_all_possible_allocs_time-get_possible_comps_time)
        allocs.sort(key=lambda x: -x[2])

        max_ev_alloc = None
        for alloc in allocs:
            alloc_bosses = [comp.boss for comp in alloc[1]]
            if boss_preference and boss_preference not in alloc_bosses:
                continue
            max_ev_alloc = alloc
            break

        max_alloc_bosses = [comp.boss for comp in max_ev_alloc[1]]
        return_allocs = [max_ev_alloc + (None, )]
        for i in range(1, 6):
            if i not in max_alloc_bosses or (boss_preference and i == boss_preference):
                continue
            return_allocs.append(self.get_max_alloc_for_boss(i, allocs, boss_preference) + (i, ))
        #get_recommended_allocs_time = time.time()
        #print(get_recommended_allocs_time-get_all_possible_allocs_time)
        return return_allocs


    def get_max_alloc_for_boss(self, exclude_boss, allocs, boss_focus=None):
        max_ev_for_boss = 0
        max_alloc = None
        for alloc in allocs:
            alloc_bosses = [comp.boss for comp in alloc[1]]
            if 'D504' in alloc[0] or 'D505' in alloc[0]:
                continue
            if exclude_boss in alloc_bosses:
                continue
            if boss_focus and boss_focus not in alloc_bosses:
                continue
            if alloc[2] > max_ev_for_boss:
                max_ev_for_boss = alloc[2]
                max_alloc = alloc
            '''for comp in alloc[1]:
                comp_ev = float(comp.ev[0:-1])
                if float(comp.ev[0:-1]) > max_ev_for_boss:
                    max_ev_for_boss = comp_ev
                    max_alloc = alloc'''
        return max_alloc

    '''
    Create unit count set with all units
    Borrow lets you -1 to units
    If all units == 1, then the allocation is valid except in special cases
    This broad check wil run 5 units * 5 units * 3C2 = 75 operations.
    
    Special cases where this won't work is if there are three of the same unit on two different teams
    OR if a comp is locked into a borrow and shares two units with another comp
    OR if two comps are locked into a borrow and share one unit with another comp
    So we just have to check for these special case
    Likewise this special check will do comparisons between each of the comps resulting in 75 operations.
    '''
    def evaluate_alloc(self, comps):
        number_of_borrows = 0
        units_map = {}
        excess = 0
        broad_check = True
        special_checks = True
        for comp in comps:
            if not comp.borrow:
                number_of_borrows += 1
            for unit in comp.units:
                if unit in units_map:
                    excess += 1
                else:
                    units_map[unit] = 1
        if number_of_borrows < excess:
            broad_check = False

        for i in range(3):
            for j in range(i+1, 3):
                '''if comps[j].tl_code == 'D30':
                    print('hi')'''
                count = comps[i].compare_count(comps[j])
                #print(f'{comps[i].tl_code}, {comps[j].tl_code}, {count}')
                if comps[i].borrow and comps[j].borrow and count >= 1:
                    special_checks = False
                    break
                elif (comps[i].borrow or comps[j].borrow) and count >= 2:
                    special_checks = False
                    break
                elif count >= 3:
                    special_checks = False
                    break

        return broad_check and special_checks


    def satisfies_filters(self, alloc, tl_filters):
        satisfies_filters = True
        for tl_filter in tl_filters[1]:
            tl_code_split = alloc[0].split(',')
            if tl_filter not in tl_code_split:
                satisfies_filters = False
                break
        return satisfies_filters

    def get_valid_converted_alloc(self, tl, no_manual=False, same_boss_alloc=True, improve_score=False):
        valid_allocs = []

        # TL already allocated, cannot convert
        if tl in [self.comp1.tl_code, self.comp2.tl_code, self.comp3.tl_code]:
            return None

        alloced_bosses = [self.comp1.tl_code[1], self.comp2.tl_code[1], self.comp3.tl_code[1]]
        tl_filters1 = None
        tl_filters2 = None
        tl_filters3 = None
        tl_filters = []
        if same_boss_alloc or tl[1] not in alloced_bosses:
            tl_filters1 = (self.comp3.tl_code, [tl, self.comp1.tl_code, self.comp2.tl_code])
            tl_filters2 = (self.comp1.tl_code, [tl, self.comp2.tl_code, self.comp3.tl_code])
            tl_filters3 = (self.comp2.tl_code, [tl, self.comp1.tl_code, self.comp3.tl_code])
            tl_filters = [tl_filters1, tl_filters2, tl_filters3]
        else:
            if self.comp3.tl_code[1] == tl[1]:
                tl_filters1 = (self.comp3.tl_code, [tl, self.comp1.tl_code, self.comp2.tl_code])
                tl_filters.append(tl_filters1)
            if self.comp1.tl_code[1] == tl[1]:
                tl_filters2 = (self.comp1.tl_code, [tl, self.comp2.tl_code, self.comp3.tl_code])
                tl_filters.append(tl_filters2)
            if self.comp2.tl_code[1] == tl[1]:
                tl_filters3 = (self.comp2.tl_code, [tl, self.comp1.tl_code, self.comp3.tl_code])
                tl_filters.append(tl_filters3)
        possible_comps = self.get_possible_comps(no_manual)
        allocs = self.get_all_possible_allocs(possible_comps, same_boss_alloc, tl_filters)
        #if self.user.lower() == 'zalteo':
        #    print('zalteo')

        for alloc in allocs:
            #if 'D45' in alloc[0]:
            #    print('test')
            if tl_filters1 and self.satisfies_filters(alloc, tl_filters1):
                valid_allocs.append((tl_filters1[0], alloc))
            if tl_filters2 and self.satisfies_filters(alloc, tl_filters2):
                valid_allocs.append((tl_filters2[0], alloc))
            if tl_filters3 and self.satisfies_filters(alloc, tl_filters3):
                valid_allocs.append((tl_filters3[0], alloc))

        return valid_allocs

    def __str__(self):
        if self.roster_box:
            return f"User: {self.user}\nRoster Box: {self.roster_box}"
        else:
            return f"User: {self.user}"

def construct_homework_grid(i, j, values):
    COL_OFFSET = 12
    ROW_OFFSET = 21
    grid = []
    user = values[i][j + 4]
    for row in range(i, i + ROW_OFFSET):
        grid.append(values[row][j:j+COL_OFFSET])
    #print(grid)
    return user, grid


def get_homework(chorry=False, cache=False):
    if not cache:
        hw_wksht = get_homework_worksheet(chorry)
        values = hw_wksht.get_all_values()

        homework = []
        for i in range(len(values)):
            for j in range(len(values[i])):
                if values[i][j] == '#':
                    user, grid = construct_homework_grid(i, j, values)
                    homework.append(Homework(user, grid))

        return homework
    else:
        homework = SqliteDict(sqlitedict_base_path + 'homework.sqlite', autocommit=True)
        return homework['chorry' if chorry else 'worry']


def convert_ev_to_float(ev):
    ev_as_num = ''
    for c in ev:
        if c.isnumeric() or c == '.':
            ev_as_num += c
        else:
            break
    if ev_as_num == '':
        return 0
    return float(ev_as_num)


def load_roster_from_sheets(user, chorry):
    rosters = SqliteDict(sqlitedict_base_path + 'rosters.sqlite', autocommit=True)

    if chorry:
        if 'chorry' in rosters:
            rosters_dict = rosters['chorry']
        else:
            rosters_dict = {}
    else:
        if 'worry' in rosters:
            rosters_dict = rosters['worry']
        else:
            rosters_dict = {}
    if user == 'all':
        roster_idx = 11
        while True:
            try:
                sht = sheets_helper.get_roster_worksheet_by_idx(roster_idx, chorry)
                if sht:
                    user = sht.title.lower()
                    hw = Homework(sht.title, None, None, sht)
                    print(hw)
                    rosters_dict[user] = hw
                roster_idx += 1
            except pygsheets.exceptions.WorksheetNotFound:
                break
        for roster in rosters:
            print(roster)
    elif user == 'reset':
        rosters['worry' if not chorry else 'chorry'] = {}
        return
    else:
        hw = Homework(user, None, None)
        rosters_dict[user.lower()] = hw
    rosters['worry' if not chorry else 'chorry'] = rosters_dict


def get_roster(user):
    rosters = SqliteDict(sqlitedict_base_path + 'rosters.sqlite', autocommit=True)
    #worry_roster = rosters['worry']
    lowercase_user = user.lower()
    if lowercase_user in rosters['worry']:
        return rosters['worry'][lowercase_user]
    if lowercase_user in rosters['chorry']:
        return rosters['chorry'][lowercase_user]
    return None


def save_homework(chorry):
    homework = SqliteDict(sqlitedict_base_path + 'homework.sqlite', autocommit=True)
    hw = get_homework(chorry)
    if chorry:
        homework['chorry'] = hw
    else:
        homework['worry'] = hw


def background_save_homework():
    first_run = True
    while True:
        if first_run:
            # Extra delay to desync from other load thread
            sleep(60)
            first_run = False
        print('Background saving homework sheet for worry')
        save_homework(False)
        sleep(360)
        print('Background saving homework sheet for chorry')
        save_homework(True)
        sleep(360)


def get_banned_tls():
    banned_tls = SqliteDict(sqlitedict_base_path + 'banned_tls.sqlite', autocommit=True)
    #print(banned_tls['banned'])
    return banned_tls['banned']


def add_banned_tl(id):
    banned_tls = SqliteDict(sqlitedict_base_path + 'banned_tls.sqlite', autocommit=True)
    if 'banned' not in banned_tls:
        banned_tls['banned'] = []
    banned_tls['banned'].append(id)
    banned = banned_tls['banned']
    banned.append(id)
    banned_tls['banned'] = banned

#add_banned_tl("D51")
def reset_banned_tls():
    banned_tls = SqliteDict(sqlitedict_base_path + 'banned_tls.sqlite', autocommit=True)
    banned_tls['banned'] = []


#save_homework(False)
#load_roster('all', False)
#print(get_roster('zalteo'))
#hw = Homework('ErnLe', None, None)
#print(hw.get_recommended_allocs(boss_preference=3))