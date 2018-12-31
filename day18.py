""" Solution to day 18 of the 2018 Advent of Code """

import logging

import numpy as np

from utils import read_input, parse_args, ASCIIVideoBuilder

OPEN_GROUND = ord('.')
TREES = ord('|')
LUMBERYARD = ord('#')

COLOR_MAP = {
    OPEN_GROUND: (0, 0, 0),
    TREES: (0, 255, 0),
    LUMBERYARD: (255, 0, 0)
}


class Area:
    """ Class representing the development area """

    def __init__(self, lines, build_video=False):
        text = "\n".join(lines)

        self.rows = len(lines)
        self.cols = len(lines[0])
        self._acres = np.array([[ord(char) for char in line]
                                for line in lines], np.uint8)
        self._acres = np.pad(self._acres, ((1, 1), (1, 1)), "constant")
        self._buffer = np.zeros_like(self._acres)

        if build_video:
            self._builder = ASCIIVideoBuilder(
                "day18.mp4", self._acres[1:-1, 1:-1], COLOR_MAP)
        else:
            self._builder = None

        assert str(self) == text, "{}\n{}".format(str(self), text)

    def __repr__(self):
        area = self._acres[1:-1, 1:-1]
        lines = [[chr(ord) for ord in row] for row in area]
        return "\n".join(["".join(line) for line in lines])

    def _acre_update(self, row, col):
        """ Determine how the acre at (row col) should update """
        neighbors = self._acres[row:row+3, col:col+3]
        acre = neighbors[1, 1]
        if acre == OPEN_GROUND:
            if np.sum(neighbors == TREES) >= 3:
                return TREES

            return OPEN_GROUND

        if acre == TREES:
            if np.sum(neighbors == LUMBERYARD) >= 3:
                return LUMBERYARD

            return TREES

        if acre == LUMBERYARD:
            num_trees = np.sum(neighbors == TREES)
            num_yards = np.sum(neighbors == LUMBERYARD)
            if num_trees and num_yards > 1:
                return LUMBERYARD

            return OPEN_GROUND

        raise ValueError("Invalid value {} at {}".format(acre, (row, col)))

    def update(self):
        """ Update the area by one minute """

        if self._builder:
            self._builder.add_frame(self._acres[1:-1, 1:-1])

        self._buffer[:] = 0
        for row in range(self.rows):
            for col in range(self.cols):
                self._buffer[row+1, col+1] = self._acre_update(row, col)

        self._acres, self._buffer = self._buffer, self._acres

    def close(self):
        """ Release any resources held by this object """

        if self._builder:
            self._builder.close()
            self._builder = None

    @property
    def total_resource_value(self):
        """ The total resource value of the area """
        return np.sum(self._acres == TREES) * np.sum(self._acres == LUMBERYARD)


def simulate(area, num_minutes):
    """ Simulate the log-cutting process """
    for minute in range(num_minutes):
        logging.debug("\nMinute %d", minute)
        logging.debug("%s", area)

        area.update()

    return area.total_resource_value


def find_longest_common_subsequence(values):
    """ Find the longest repeated subsequence in a list """
    max_length = 0
    start = None
    for length in range(5, 50):
        valid = None
        for start in range(len(values) - length):
            next_start = start + length
            match = True
            for i in range(length):
                if values[start+i] != values[next_start+i]:
                    match = False
                    break

            if match:
                valid = start
                break

        if valid:
            max_length = length
            start = valid
            logging.debug("Found sequence of length %d at %d", length, valid)

    return max_length, start


def discover_pattern(area, num_samples):
    """ Find the pattern in the log-cutting cycle """
    minutes = []
    values = []
    for minute in range(num_samples):
        minutes.append(minute)
        values.append(area.total_resource_value)

        area.update()

        logging.debug("%d: %d", minute, values[-1])

    length, start = find_longest_common_subsequence(values)
    sequence = values[start:start+length]
    logging.debug("Found sequence: %s", sequence)
    logging.debug("Verifying prediction...")

    for test in range(100):
        minute = num_samples + test
        expected = sequence[(minute - start) % length]
        actual = area.total_resource_value

        assert actual == expected

        area.update()

    return sequence[(1000000000 - start) % length]


def test_day18():
    """ Test for day 18 """
    lines = read_input(18, True)
    area = Area(lines)

    expected = 1147
    actual = simulate(area, 10)
    assert actual == expected

def day18():
    """ Solution to day 18 """
    args = parse_args()

    lines = read_input(18)

    if args.num_video_frames > 0:
        area = Area(lines, True)
        num_updates = args.num_video_frames
    else:
        area = Area(lines)
        num_updates = 10

    print("Part 1")
    print(simulate(area, num_updates))

    area.close()

    if args.num_video_frames:
        return

    area = Area(lines)
    print("Part 2")
    print(discover_pattern(area, 600))


if __name__ == "__main__":
    day18()
