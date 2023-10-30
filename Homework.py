from sheets_helper import get_homework_worksheet


class Composition:
    def __init__(self, units, tl_code, ev, borrow):
        self.units = units
        self.tl_code = tl_code
        self.ev = ev
        self.borrow = borrow

    def __str__(self):
        return f'Units: {str(self.units)}\nTL Code: {self.tl_code}\nEV:{self.ev}\nBorrow:{self.borrow}'

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

    def __init__(self, user, homework_grid):
        self.user = user
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


def construct_homework_grid(i, j, values):
    COL_OFFSET = 12
    ROW_OFFSET = 21
    grid = []
    user = values[i][j + 4]
    for row in range(i, i + ROW_OFFSET):
        grid.append(values[row][j:j+COL_OFFSET])
    print(grid)
    return user, grid


def get_homework():
    hw_wksht = get_homework_worksheet()
    values = hw_wksht.get_all_values()

    homework = []
    for i in range(len(values)):
        for j in range(len(values[i])):
            if values[i][j] == '#':
                user, grid = construct_homework_grid(i, j, values)
                homework.append(Homework(user, grid))

    return homework

get_homework()