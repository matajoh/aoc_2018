""" Solution to day 17 of the 2018 Advent of Code """

import logging
from collections import deque

import numpy as np

from utils import read_input, parse_args, temp_file, Point, VideoBuilder

SAND = '.'
CLAY = '#'
WATER = '~'
SPRING = '+'
FLOWING = '|'

COLOR_MAP = {
    ord(SAND): (0, 0, 0),
    ord(CLAY): (255, 0, 0),
    ord(WATER): (0, 0, 255),
    ord(SPRING): (255, 255, 255),
    ord(FLOWING): (0, 255, 255)
}
FRAME_SKIP = 2


DOWN = Point(1, 0)
LEFT = Point(0, -1)
RIGHT = Point(0, 1)


class Drop(Point):
    """ Class representing water that is dropping vertically """

    def __init__(self, row, col):
        super().__init__(row, col)
        self._left = None
        self._right = None
        self._flowed = False

    def __add__(self, other):
        return Drop(self.row + other.row, self.col + other.col)

    @property
    def left(self):
        """ The left-most spread of this drop """
        return self._left

    @left.setter
    def left(self, col):
        self._left = col

    @property
    def right(self):
        """ The right-most spread of this drop """
        return self._right

    @right.setter
    def right(self, col):
        self._right = col

    def flow(self, clay, water, flowing, max_row):
        """ Flows this water, resulting in other water objects """
        if self in water:
            return None

        flowing.add(self)
        down = self + DOWN
        if down in clay or down in water:
            if self._flowed:
                if self._left and self._right:
                    for col in range(self._left, self._right + 1):
                        point = Point(self.row, col)
                        flowing.remove(point)
                        water.add(point)

                return None

            self._flowed = True
            return self, Flow(self.row, self.col, False, self), Flow(self.row, self.col, True, self)

        elif down not in flowing and down.row < max_row:
            return [self, down]

        return None


class Flow(Point):
    """ Class representing water that is flowing horizontally """

    def __init__(self, row, col, flow_left, drop):
        super().__init__(row, col)
        self._flow_left = flow_left
        self._drop = drop

    def __add__(self, other):
        return Flow(self.row + other.row, self.col + other.col, self._flow_left, self._drop)

    def flow(self, clay, water, flowing, max_row):
        """ Flows the water, resulting in other water objects """
        if self in water:
            if self._flow_left:
                self._drop.left = self.col
            else:
                self._drop.right = self.col

            return None

        flowing.add(self)
        down = self + DOWN
        if self._flow_left:
            left = self + LEFT
            if left in clay or left in water:
                self._drop.left = self.col
                return None

            if down in clay or down in water:
                return [left]
        else:
            right = self + RIGHT
            if right in clay or right in water:
                self._drop.right = self.col
                return None

            if down in clay or down in water:
                return [right]

        if down in flowing:
            return None

        if down.row < max_row:
            return [Drop(self.row, self.col)]

        return None


def line_to_points(line):
    """ Converts a line representation to a iterable of points """
    parts = line.split(',')
    val0 = int(parts[0][2:])
    parts = parts[1].strip()[2:].split('..')
    val1 = int(parts[0])
    val2 = int(parts[1])
    if line.startswith('x'):
        for y in range(val1, val2 + 1):
            yield Point(y, val0)
    elif line.startswith('y'):
        for x in range(val1, val2 + 1):
            yield Point(val0, x)
    else:
        raise ValueError("Invalid input: " + line)


class Ground:
    """ Class representing the ground and its water table """

    def __init__(self, lines):
        self._clay = set()
        self._water = set()
        self._flowing = set()
        self._out_of_range = set()
        self._rows = 0
        self._min_row = 10000
        self._min_col = 500
        self._max_col = 500
        for line in lines:
            for point in line_to_points(line):
                self._clay.add(point)
                self._min_row = min(self._min_row, point.row)
                self._min_col = min(self._min_col, point.col)
                self._max_col = max(self._max_col, point.col)
                self._rows = max(self._rows, point.row)

        self._rows += 1
        self._min_col -= 1
        self._max_col += 1
        self._cols = self._max_col - self._min_col + 1

    def flow(self, build_video):
        """ Flows water through the ground from the spring """
        if build_video:
            state = np.zeros((self._rows, self._cols), np.uint8)
            state[:] = ord(SAND)
            for clay in self._clay:
                state[clay.row, clay.col - self._min_col] = ord(CLAY)
            state[0, 500 - self._min_col] = ord(SPRING)

            builder = VideoBuilder("day17.mp4", state, COLOR_MAP, 60)
        else:
            state = None
            builder = None

        frontier = [Drop(1, 500)]
        last_report = 0
        frame_skip = 0
        while frontier:
            water = frontier.pop()
            outflow = water.flow(self._clay, self._water,
                                 self._flowing, self._rows)

            if build_video:
                if frame_skip:
                    frame_skip -= 1
                else:
                    for flowing in self._flowing:
                        col = flowing.col - self._min_col
                        state[flowing.row, col] = ord(FLOWING)

                    for water in self._water:
                        col = water.col - self._min_col
                        state[water.row, col] = ord(WATER)

                    builder.add_frame(state)
                    frame_skip = FRAME_SKIP

            if self.reachable_tiles - last_report > 5:
                logging.debug(self.reachable_tiles)
                last_report = self.reachable_tiles

            if outflow:
                for flow in outflow:
                    if flow.row < self._min_row:
                        self._out_of_range.add(flow)
                    frontier.append(flow)

        if build_video:
            builder.close()

    def __repr__(self):
        lines = [[SAND for _ in range(self._cols)] for _ in range(self._rows)]
        lines[0][500 - self._min_col] = SPRING
        for row, col in self._clay:
            lines[row][col - self._min_col] = CLAY

        for row, col in self._water:
            lines[row][col - self._min_col] = WATER

        for row, col in self._flowing:
            lines[row][col - self._min_col] = FLOWING

        return "\n".join(["".join(line) for line in lines])

    @property
    def reachable_tiles(self):
        """ Returns the number of tiles the water reaches """
        return len(self._flowing) + len(self._water) - len(self._out_of_range)

    @property
    def remaining_water(self):
        """ Returns the amount of water that will remain once the spring dries up """
        return len(self._water)


def parse_input(lines):
    """ Parses the input """
    lines = deque(lines)
    text = []
    while lines:
        line = lines.popleft().strip()
        if not line:
            break

        text.append(line)

    return text


def parse_repr(lines):
    """ Parses the debug representation """
    lines = deque(lines)
    while lines:
        line = lines.popleft().strip()
        if not line:
            break

    text = []
    while lines:
        text.append(lines.popleft().strip())

    return "\n".join(text)


def test_day17():
    """ Test for day 17 """
    lines = read_input(17, True)
    ground = Ground(parse_input(lines))

    actual = str(ground)
    expected = parse_repr(lines)
    assert actual == expected

    ground.flow(False)

    expected = 57
    actual = ground.reachable_tiles
    assert actual == expected

    expected = 29
    actual = ground.remaining_water
    assert actual == expected


def day17():
    """ Solution to day 17 """
    args = parse_args()
    lines = read_input(17)
    ground = Ground(parse_input(lines))

    ground.flow(args.video)

    with open(temp_file("ground.txt"), "w") as file:
        file.write(str(ground))

    print("Part 1")
    print("Reachable tiles:", ground.reachable_tiles)

    print("Part 2")
    print("Remaining water:", ground.remaining_water)


if __name__ == "__main__":
    day17()
