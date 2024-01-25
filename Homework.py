import sheets_helper
from sheets_helper import get_homework_worksheet
from Timelines import get_single_boss_timelines_from_db
from icon_bank import clean_text, shorten_name
#import time

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

    def __init__(self, user, homework_grid=None, roster_box=None):
        self.user = user
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
                self.load_units_available()

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

    def load_units_available(self):
        roster_start_tuple = (4, 2)
        roster_end_tuple = (254, 5)

        roster_worksheet = sheets_helper.get_roster_worksheet(self.user if self.user[0].isupper() else self.user.capitalize())
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
    def get_all_possible_allocs(self, possible_comps):
        allocs = []
        for boss1 in range(1, 6):
            for boss2 in range(boss1+1, 6):
                if boss1 >= boss2:
                    continue
                for boss3 in range(boss2+1, 6):
                    if boss2 >= boss3:
                        continue
                    for comp1 in possible_comps[boss1]:
                        for comp2 in possible_comps[boss2]:
                            for comp3 in possible_comps[boss3]:
                                alloc = [possible_comps[boss1][comp1], possible_comps[boss2][comp2], possible_comps[boss3][comp3]]
                                if self.evaluate_alloc(alloc):
                                    total_ev = 0
                                    ids = ','.join([comp.tl_code for comp in alloc])
                                    for comp in alloc:
                                        total_ev += convert_ev_to_float(comp.ev)
                                    allocs.append((ids, alloc, total_ev))
        return allocs


    def get_recommended_allocs(self, no_manual=False, boss_preference=None):
        #start = time.time()
        possible_comps = self.get_possible_comps(no_manual)
        #get_possible_comps_time = time.time()
        #print(get_possible_comps_time - start)
        allocs = self.get_all_possible_allocs(possible_comps)
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
        '''elif boss_preference:
            max_alloc = self.get_max_alloc_for_boss(boss_preference, allocs)
            return max_alloc
        else:
            allocs.sort(key = lambda x: -x[2])
            return allocs[-1]'''


    def get_max_alloc_for_boss(self, exclude_boss, allocs, boss_focus=None):
        max_ev_for_boss = 0
        max_alloc = None
        for alloc in allocs:
            alloc_bosses = [comp.boss for comp in alloc[1]]
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

def construct_homework_grid(i, j, values):
    COL_OFFSET = 12
    ROW_OFFSET = 21
    grid = []
    user = values[i][j + 4]
    for row in range(i, i + ROW_OFFSET):
        grid.append(values[row][j:j+COL_OFFSET])
    #print(grid)
    return user, grid


def get_homework(chorry=False):
    hw_wksht = get_homework_worksheet(chorry)
    values = hw_wksht.get_all_values()

    homework = []
    for i in range(len(values)):
        for j in range(len(values[i])):
            if values[i][j] == '#':
                user, grid = construct_homework_grid(i, j, values)
                homework.append(Homework(user, grid))

    return homework


def convert_ev_to_float(ev):
    ev_as_num = ''
    for c in ev:
        if c.isnumeric() or c == '.':
            ev_as_num += c
        else:
            break
    return float(ev_as_num)

#hw = Homework('ErnLe', None, None)
#print(hw.get_recommended_allocs(boss_preference=3))