""" Solution to day 22 of the 2018 Advent of Code """

from collections import namedtuple

import numpy as np

from utils import parse_args, read_input, diff, AStarSearch

DEBUG = (510, (10, 10))
INPUT = (11991, (6, 797))

ROCKY = 0
WET = 1
NARROW = 2

MODULO = 20183
ROW_MULTIPLER = 48271
COL_MULTIPLIER = 16807

NEITHER = 0
CLIMBING_GEAR = 1
TORCH = 2

TOOLS = [
    set([CLIMBING_GEAR, TORCH]),
    set([CLIMBING_GEAR, NEITHER]),
    set([TORCH, NEITHER])
]

TOOL_SWITCH = 7


def distance_between(pos0, pos1):
    """ Computes the distance between two positions """
    if pos0.tool != pos1.tool:
        return TOOL_SWITCH

    return 1


def other_tool(risk_level, tool):
    """ Determines the other tool available at the current risk level """
    if risk_level == ROCKY:
        if tool == CLIMBING_GEAR:
            return TORCH

        if tool == TORCH:
            return CLIMBING_GEAR

        raise ValueError

    if risk_level == WET:
        if tool == CLIMBING_GEAR:
            return NEITHER

        if tool == NEITHER:
            return CLIMBING_GEAR

        raise ValueError

    if risk_level == NARROW:
        if tool == TORCH:
            return NEITHER

        if tool == NEITHER:
            return TORCH

        raise ValueError

    raise ValueError


def heuristic(pos, goal):
    """ The A* heuristic """
    distance = abs(pos.row-goal.row) + abs(pos.col - goal.col)
    return distance


class Position(namedtuple("Position", ("row", "col", "risk_level", "tool"))):
    """ Class representing a position in the cave """

    def neighbors(self, cave):
        """ Returns all the valid neighbors of this position """
        yield Position(self.row, self.col, self.risk_level, other_tool(self.risk_level, self.tool))

        for drow, dcol in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            rrow = self.row + drow
            ccol = self.col + dcol
            if rrow < 0 or ccol < 0:
                continue

            risk_level = cave.risk_level(rrow, ccol)
            tools = TOOLS[risk_level]
            if self.tool in tools:
                yield Position(rrow, ccol, risk_level, self.tool)


class Cave:
    """ Class representing the cave system """

    def __init__(self, depth, target):
        self._erosion_levels = {}
        self._depth = depth
        self._target = target
        self._erosion_levels[(0, 0)] = depth % MODULO
        self._erosion_levels[target] = depth % MODULO

    def get_erosion_level(self, row, col):
        """ Returns the erosion level at (row col) """
        return self._compute_erosion(row, col)

    def risk_level(self, row, col):
        """ Returns the risk level at (row, col) """
        return self._compute_erosion(row, col) % 3

    def compute_total_risk(self):
        """ Computes the total risk of the cave """
        total = 0
        rows, cols = self._target
        rows += 1
        cols += 1
        for row in range(rows):
            for col in range(cols):
                total += self.risk_level(row, col)

        return total

    def _compute_erosion(self, row, col):
        """ Computes the erosion level at (row, col) """
        pos = (row, col)
        if pos in self._erosion_levels:
            return self._erosion_levels[pos]

        if row == 0:
            index = col * COL_MULTIPLIER
        elif col == 0:
            index = row * ROW_MULTIPLER
        else:
            north = self._compute_erosion(row-1, col)
            west = self._compute_erosion(row, col-1)
            index = north * west

        self._erosion_levels[pos] = (index + self._depth) % MODULO
        return self._erosion_levels[pos]

    def neighbors(self, position):
        """ Returns the valid neighbors of a position """
        return position.neighbors(self)

    def find_shortest_path(self):
        """ Finds the shortest path to the target """
        goal = Position(self._target[0], self._target[1], ROCKY, TORCH)
        start = Position(0, 0, ROCKY, TORCH)

        search = AStarSearch(heuristic, distance_between, self)
        return search.find_shortest_path(start, goal)


def to_string(cave, target, rows, cols):
    """ Converts the cave to a string """
    risk_level = np.zeros((rows, cols), np.uint8)
    for row in range(rows):
        for col in range(cols):
            risk_level[row, col] = cave.get_erosion_level(row, col) % 3

    risk_level[risk_level == 0] = ord('.')
    risk_level[risk_level == 1] = ord('=')
    risk_level[risk_level == 2] = ord('|')
    risk_level[0, 0] = ord('M')
    risk_level[target] = ord('T')

    lines = [[chr(region) for region in row] for row in risk_level]
    return "\n".join(["".join(line) for line in lines])


def test_day22():
    """ Tests the code """
    depth, (col, row) = DEBUG
    target = row, col

    cave = Cave(depth, target)
    expected = read_input(22, True, no_split=True)
    actual = to_string(cave, target, 16, 16)
    assert actual == expected, diff(actual, expected)

    expected = 114
    actual = cave.compute_total_risk()
    assert actual == expected, "{} != {}".format(actual, expected)

    expected = 45
    path = cave.find_shortest_path()
    actual = 0
    current = path[0]
    for pos in path[1:]:
        actual += distance_between(current, pos)
        current = pos

    assert actual == expected, "{} != {}".format(actual, expected)


def part1():
    """ Solution to part 1 """
    depth, (col, row) = INPUT
    cave = Cave(depth, (row, col))
    return cave.compute_total_risk()


def part2():
    """ Solution to part 2 """
    depth, (col, row) = INPUT
    cave = Cave(depth, (row, col))
    path = cave.find_shortest_path()
    time = 0
    current = path[0]
    for pos in path[1:]:
        time += distance_between(current, pos)
        current = pos

    return time


def day22():
    """ Solution to day 22 """
    parse_args()

    print("Part 1")
    print(part1())

    print("Part 2")
    print(part2())


if __name__ == "__main__":
    day22()
