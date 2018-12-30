""" Solution to day 15 of the 2018 Advent of Code """

import logging
from collections import deque

import numpy as np

from utils import read_input, parse_args, VideoBuilder, AStarSearch, diff

PART1_TEST_OUTCOMES = [
    27730,
    36334,
    39514,
    27755,
    28944,
    18740
]

PART2_TEST_OUTCOMES = [
    (15, 4988),
    (4, 29064),
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

COLOR_MAP = {
    CLEAR: (0, 0, 0),
    WALL: (255, 255, 255),
    ELF: (0, 255, 0),
    GOBLIN: (255, 0, 0)
}


class ElfException(Exception):
    """ Exception thrown when an elf dies """

    def __init__(self):
        super().__init__("Elf Exception")


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
                 raise_on_elf_death=False,
                 build_video=False):
        lines = [[ord(char) for char in line] for line in lines]
        lines = np.array(lines)

        self._num_rounds = 0
        self._max_dist = np.prod(lines.shape)
        self._walls = lines == WALL
        self._units = np.zeros(lines.shape, np.dtype(Unit))
        self._raise_on_elf_death = raise_on_elf_death
        self._search = AStarSearch(heuristic, lambda a, b: 1, self)
        for ravel, spec in enumerate(lines.flatten()):
            index = np.unravel_index(ravel, lines.shape)
            if spec not in (ELF, GOBLIN):
                self._units[index] = None
            else:
                attack_power = elf_attack_power if spec == ELF else DEFAULT_ATTACK
                self._units[index] = Unit(
                    spec, self, index, attack=attack_power)

        if build_video:
            self._builder = VideoBuilder("day15.mp4", self._walls, COLOR_MAP)
            self._state = np.zeros_like(self._walls, np.uint8)
        else:
            self._builder = None
            self._state = None

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

    def neighbors(self, position):
        """ Returns the valid neighbors for a position """
        for neighbor in neighbors(position):
            if self._walls[neighbor]:
                continue

            if self._units[neighbor]:
                continue

            yield neighbor

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
        return self._search.find_shortest_path(start, goal)

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

    def _add_frame(self):
        self._state[self._walls == 1] = WALL
        self._state[self._walls == 0] = CLEAR
        for unit in self._units.flatten():
            if unit is None or not unit.is_alive:
                continue

            self._state[unit.index] = unit.race

        self._builder.add_frame(self._state)

    def round(self):
        """ Performs a round of combat """
        if self._builder:
            self._add_frame()

        units = self._units.flatten().tolist()
        for i, unit in enumerate(units):
            if unit is None or not unit.is_alive:
                continue

            if self._state:
                self._state[unit.index] = unit.race

            if unit.take_turn():
                if i == len(units) - 1:
                    self._num_rounds += 1

                if self._builder:
                    self._add_frame()
                    self._builder.close()

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

    return "\n".join(start_lines)


def read_end_state(lines):
    """ Reads the ending state from the provided lines """
    end_lines = []
    while lines:
        line = lines.popleft().strip()
        if not line:
            break

        end_lines.append(line)

    return "\n".join(end_lines)


def run_battle(battle):
    """ Runs a battle to completion """
    logging.debug("Round %d", battle.num_rounds)
    logging.debug("%s", battle)

    while not battle.round():
        logging.debug("Round %d", battle.num_rounds)
        logging.debug("%s", battle)

    logging.debug("Final")
    logging.debug("%s", battle)


def determine_outcome(build_video):
    """ Determine the outcome of the battle """
    lines = deque(read_input(15))

    expected = read_start_state(lines)
    battle = Battle(expected.split('\n'), build_video=build_video)
    assert battle.to_string(True) == expected

    run_battle(battle)

    _, hp_sum = battle.winners
    return hp_sum * battle.num_rounds


def test_part1():
    """ Test for part 1 """
    lines = read_input(15, True)
    lines = deque(lines)
    outcomes0 = PART1_TEST_OUTCOMES

    case = 0
    while lines:
        expected = read_start_state(lines)
        battle = Battle(expected.split('\n'), build_video=False)
        assert battle.to_string(True) == expected

        expected = read_end_state(lines)
        run_battle(battle)
        assert str(battle) == expected, diff(str(battle), expected)

        _, hp_sum = battle.winners
        actual = hp_sum * battle.num_rounds
        assert actual == outcomes0[case]

        case += 1


def try_attack_power(expected, attack_power):
    """ Try the provided attack power """
    battle = Battle(expected.split('\n'), attack_power, True)
    try:
        run_battle(battle)
        return battle
    except ElfException:
        return None


def find_attack_power():
    """ Find an attack power so that the elves win """
    lines = deque(read_input(15))

    expected = read_start_state(lines)
    attack_power = 4
    while True:
        battle = try_attack_power(expected, attack_power)
        if battle is None:
            logging.debug("%d failed, trying %d",
                          attack_power, attack_power + 1)

            attack_power += 1
            continue

        _, hp_sum = battle.winners
        return hp_sum * battle.num_rounds


def test_part2():
    """ Test for part 2"""
    lines = deque(read_input(15, True))
    outcomes1 = PART2_TEST_OUTCOMES

    case = 0
    while lines:
        expected = read_start_state(lines)
        read_end_state(lines)

        attack_power = 4
        while True:
            battle = try_attack_power(expected, attack_power)
            if battle is None:
                logging.debug("%d failed, trying %d",
                              attack_power, attack_power + 1)

                attack_power += 1
                continue

            _, hp_sum = battle.winners
            expected_ap, expected = outcomes1[case]
            actual = hp_sum * battle.num_rounds
            assert attack_power == expected_ap
            assert actual == expected
            break

        case += 1


def day15():
    """ Solution to day 15 """
    args = parse_args()

    print("Part 1")
    print(determine_outcome(args.video))

    if args.video:
        return

    print("Part 2")
    print(find_attack_power())


if __name__ == "__main__":
    day15()
