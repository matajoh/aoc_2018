""" Solution to day 15 of the 2018 Advent of Code """

from collections import deque

import numpy as np

from utils import read_input, parse_args

DEBUG_PART1_OUTCOMES = [
    27730,
    36334,
    39514,
    27755,
    28944,
    18740
]

DEBUG_PART2_OUTCOMES = [
    (15, 4988),
    (0, None),
    (4, 31284),
    (15, 3478),
    (12, 6474),
    (34, 1140)
]

CLEAR = ord('.')
WALL = ord('#')
ELF = ord('E')
GOBLIN = ord('G')

DEFAULT_HEALTH = 200
DEFAULT_ATTACK = 3


class ElfException(Exception):
    """ Exception thrown when an elf dies """

    def __init__(self):
        super().__init__("Elf Exception")


def reconstruct_path(came_from, current):
    """ Reconstructs a path for A-star search """
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)

    return total_path


def heuristic(first, second):
    """ Manhattan distance heuristic for A-star search """
    return abs(first[0]-second[0]) + abs(first[1]-second[1])


def neighbors(point):
    """ Return the manhattan neighbors of a point """
    row, col = point
    return [
        (row - 1, col),
        (row, col-1),
        (row, col+1),
        (row+1, col)
    ]


class Unit:
    """ Class representing a unit in the battle """

    def __init__(self, race, battle, index,
                 health=DEFAULT_HEALTH, attack=DEFAULT_ATTACK):
        self._race = race
        self._battle = battle
        self._enemy = GOBLIN if race == ELF else ELF
        self._health_points = health
        self._attack_power = attack
        self._index = index

    @property
    def health_points(self):
        """ The health points of the unit """
        return self._health_points

    @property
    def race(self):
        """ The unit's race """
        return self._race

    @property
    def index(self):
        """ The location of the unit in the battle """
        return self._index

    def take_damage(self, damage):
        """ Causes the unit to take damage, possibly resulting in death """
        self._health_points -= damage
        if self._health_points <= 0:
            self._battle.remove(self)

    def __lt__(self, other):
        return self._index < other.index

    def _attack(self):
        min_hp = DEFAULT_HEALTH
        targets = []
        for neighbor in neighbors(self._index):
            other = self._battle[neighbor]
            if other is None or other.race == self._race:
                continue

            if other.health_points < min_hp:
                min_hp = other.health_points
                targets = [other]
            elif other.health_points == min_hp:
                targets.append(other)

        if targets:
            targets.sort()
            targets[0].take_damage(self._attack_power)

    def find_best_move(self, goals):
        """ Find the best move given the provided goal squares """
        min_moves = []
        min_dist = self._battle.max_dist
        goals = [(heuristic(self._index, goal), goal) for goal in goals]
        possible_moves = list(filter(self._battle.is_clear,
                                     neighbors(self._index)))
        goals.sort()
        for dist, goal in goals:
            if dist > min_dist:
                continue

            for neighbor in possible_moves:
                path = self._battle.find_min_path(neighbor, goal)
                if path is None:
                    continue

                if len(path) < min_dist:
                    min_dist = len(path)
                    min_moves = [neighbor]
                elif len(path) == min_dist:
                    min_moves.append(neighbor)

        if not min_moves:
            return None

        min_moves.sort()
        return min_moves[0]

    def _move(self, goals):
        best_move = self.find_best_move(goals)

        if best_move is None:
            return

        if self._battle.move(self, best_move):
            self._index = best_move

    def take_turn(self):
        """ Causes the unit to take its turn """
        in_range = self._battle.find_in_range(self._enemy)
        if not in_range:
            return True

        if self._index in in_range:
            self._attack()
        else:
            valid_goals = list(filter(self._battle.is_clear, in_range))
            self._move(valid_goals)
            if self._index in in_range:
                self._attack()

        return False

    @property
    def is_alive(self):
        """ Whether the unit is alive """
        return self.health_points > 0

    def __repr__(self):
        return "{}({})".format(chr(self._race), self._health_points)


class Battle:
    """ Class representing a battle simulation """

    def __init__(self, lines,
                 elf_attack_power=DEFAULT_ATTACK,
                 raise_on_elf_death=False):
        lines = [[ord(char) for char in line] for line in lines]
        lines = np.array(lines)

        self._num_rounds = 0
        self._max_dist = np.prod(lines.shape)
        self._walls = lines == WALL
        self._units = np.zeros(lines.shape, np.dtype(Unit))
        self._raise_on_elf_death = raise_on_elf_death
        for ravel, spec in enumerate(lines.flatten()):
            index = np.unravel_index(ravel, lines.shape)
            if spec not in (ELF, GOBLIN):
                self._units[index] = None
            else:
                attack_power = elf_attack_power if spec == ELF else DEFAULT_ATTACK
                self._units[index] = Unit(
                    spec, self, index, attack=attack_power)

    def to_string(self, omit_health=False):
        """ Converts the battle to a string representation """
        lines = []
        for wall_row, unit_row in zip(self._walls, self._units):
            blocks = [chr(WALL) if wall else chr(CLEAR) for wall in wall_row]

            units = []
            for col, unit in enumerate(unit_row):
                if unit:
                    blocks[col] = chr(unit.race)
                    units.append(str(unit))

            field_text = "".join(blocks)
            if omit_health:
                lines.append(field_text)
            else:
                unit_text = ", ".join(units)
                lines.append("{}   {}".format(field_text, unit_text).strip())

        return "\n".join(lines)

    @property
    def max_dist(self):
        """ The maximum distance any unit can be from another """
        return self._max_dist

    @property
    def num_rounds(self):
        """ The number of complete rounds in the battle """
        return self._num_rounds

    def find_in_range(self, race):
        """ Finds all spots adjacent to units of the provided race """
        in_range = set()
        for index, unit in enumerate(self._units.flatten()):
            if unit is None or unit.race != race:
                continue

            point = np.unravel_index(index, self._units.shape)

            for neighbor in neighbors(point):
                if not self._walls[neighbor]:
                    in_range.add(neighbor)

        return in_range

    def find_min_path(self, start, goal):
        """ Finds the minimum path from the start to the goal """
        closed_set = set()
        open_set = set([start])
        came_from = {}
        g_scores = {}
        g_scores[start] = 0
        f_scores = {}
        f_scores[start] = heuristic(start, goal)
        while open_set:
            current = None
            f_score = self._max_dist
            for point in open_set:
                if f_scores[point] < f_score:
                    f_score = f_scores[point]
                    current = point

            if current == goal:
                return reconstruct_path(came_from, current)

            open_set.remove(current)
            closed_set.add(current)

            if self._walls[current]:
                continue

            if self._units[current] and current != start:
                continue

            for neighbor in neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_scores[current] + 1
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_scores[neighbor]:
                    continue

                came_from[neighbor] = current
                g_scores[neighbor] = tentative_g_score
                f_scores[neighbor] = g_scores[neighbor] + \
                    heuristic(neighbor, goal)

        return None

    def __repr__(self):
        return self.to_string()

    def is_clear(self, index):
        """ Returns whether the provided index is a clear space """
        if self._walls[index] or self._units[index] is not None:
            return False

        return True

    def move(self, unit, index):
        """ Attempts to move the unit to the provided index """
        assert self._units[unit.index] == unit
        assert self._units[index] is None
        self._units[unit.index] = None
        self._units[index] = unit

        return True

    def remove(self, unit):
        """ Removes the unit from the battle """
        self._units[unit.index] = None
        if unit.race == ELF:
            if self._raise_on_elf_death:
                raise ElfException

    def __getitem__(self, key):
        return self._units[key]

    def round(self):
        """ Performs a round of combat """
        units = self._units.flatten().tolist()
        for i, unit in enumerate(units):
            if unit is None or not unit.is_alive:
                continue

            if unit.take_turn():
                if i == len(units) - 1:
                    self._num_rounds += 1

                return True

        self._num_rounds += 1
        return False

    @property
    def winners(self):
        """ Returns the winning race the sum of their health points """
        race = None
        hp_sum = 0
        for unit in self._units.flatten():
            if unit is None or not unit.is_alive:
                continue

            if unit.race == ELF:
                race = "Elves"
            else:
                race = "Goblins"

            hp_sum += unit.health_points

        return race, hp_sum


def read_start_state(lines):
    """ Reads the starting state from the provided lines """
    start_lines = []
    while lines:
        line = lines.popleft().strip()
        if not line:
            break

        start_lines.append(line)

    return Battle(start_lines), "\n".join(start_lines)


def read_end_state(lines):
    """ Reads the ending state from the provided lines """
    end_lines = []
    while lines:
        line = lines.popleft().strip()
        if not line:
            break

        end_lines.append(line)

    return "\n".join(end_lines)


def run_battle(battle, verbose):
    """ Runs a battle to completion """
    if verbose:
        print("Round", battle.num_rounds)
        print(battle)

    while not battle.round():
        if verbose:
            print("Round", battle.num_rounds)
            print(battle)

    if verbose:
        print("Final")
        print(battle)


def part1(debug, verbose):
    """ Solution to part 1 """
    if debug:
        lines = read_input(15, True)
        lines = deque(lines.split('\n'))
        outcomes0 = DEBUG_PART1_OUTCOMES
    else:
        lines = read_input(15)
        lines = deque(lines.split('\n'))
        outcomes0 = [None]

    case = 0
    while lines:
        battle, expected = read_start_state(lines)
        assert battle.to_string(True) == expected

        if lines:
            expected = read_end_state(lines)
        else:
            expected = None

        run_battle(battle, verbose)

        if expected:
            assert str(battle) == expected
        race, hp_sum = battle.winners
        print("Combat ends after", battle.num_rounds, "full rounds")
        print(race, "win with", hp_sum, "total hit points left")
        print("Outcome:", battle.num_rounds, "*",
              hp_sum, "=", hp_sum*battle.num_rounds)
        print("( Expected:", outcomes0[case], ")")
        case += 1


def try_attack_power(expected, attack_power):
    """ Try the provided attack power """
    battle = Battle(expected.split('\n'), attack_power, True)
    try:
        run_battle(battle, False)
        return battle
    except ElfException:
        return None


def part2(debug, verbose):
    """ Solution to part 2"""
    if debug:
        lines = read_input(15, True)
        lines = deque(lines.split('\n'))
        outcomes1 = DEBUG_PART2_OUTCOMES
    else:
        lines = read_input(15)
        lines = deque(lines.split('\n'))
        outcomes1 = [(0, None)]

    case = 0
    while lines:
        battle, expected = read_start_state(lines)
        assert battle.to_string(True) == expected
        read_end_state(lines)

        attack_power = 4
        while True:
            battle = try_attack_power(expected, attack_power)
            if battle is None:
                if verbose:
                    print(attack_power, "failed, trying", attack_power + 1)

                attack_power += 1
                continue

            race, hp_sum = battle.winners
            expected_ap, expected = outcomes1[case]
            print("Attack Power =", attack_power)
            print("Combat ends after", battle.num_rounds, "full rounds")
            print(race, "win with", hp_sum, "total hit points left")
            print("Outcome:", battle.num_rounds, "*",
                  hp_sum, "=", hp_sum*battle.num_rounds)
            print("( Expected:", expected_ap, "AP", expected, ")")
            break

        case += 1


def day15():
    """ Solution to day 15 """
    args = parse_args()

    print("Part 1")
    part1(args.debug, args.verbose)

    print("\n\nPart 2")
    part2(args.debug, args.verbose)


if __name__ == "__main__":
    day15()
