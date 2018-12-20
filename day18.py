""" Solution to day 18 of the 2018 Advent of Code """

import numpy as np

from utils import read_input, parse_args, VideoBuilder

OPEN_GROUND = ord('.')
TREES = ord('|')
LUMBERYARD = ord('#')

COLOR_MAP = {
    OPEN_GROUND: (0, 0, 0),
    TREES: (13, 55, 13),
    LUMBERYARD: (55, 27, 7)
}


class Area:
    """ Class representing the development area """

    def __init__(self, text, build_video=False):
        lines = [line.strip() for line in text.split('\n')]
        text = "\n".join(lines)

        self.rows = len(lines)
        self.cols = len(lines[0])
        self._acres = np.array([[ord(char) for char in line]
                                for line in lines], np.uint8)
        self._acres = np.pad(self._acres, ((1, 1), (1, 1)), "constant")
        self._buffer = np.zeros_like(self._acres)

        if build_video:
            self._builder = VideoBuilder(
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
        pos = (row+1, col+1)
        acre = self._acres[pos]
        if acre == OPEN_GROUND:
            if np.sum(neighbors == TREES) >= 3:
                return TREES

            return OPEN_GROUND
        elif acre == TREES:
            if np.sum(neighbors == LUMBERYARD) >= 3:
                return LUMBERYARD

            return TREES
        elif acre == LUMBERYARD:
            num_trees = np.sum(neighbors == TREES)
            num_yards = np.sum(neighbors == LUMBERYARD)
            if num_trees and num_yards > 1:
                return LUMBERYARD

            return OPEN_GROUND

        raise ValueError("Invalid value {} at {}".format(acre, pos))

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


def part1(area, num_minutes, verbose):
    """ Solution to part 1 """
    for minute in range(num_minutes):
        if verbose:
            print("\nMinute", minute)
            print(area)

        area.update()

    return area.total_resource_value


def find_longest_common_subsequence(values, verbose):
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
            if verbose:
                print("Found sequence of length", length, "at", valid)

    return max_length, start


def part2(area, num_samples, verbose):
    """ Solution to part 2 """
    minutes = []
    values = []
    for minute in range(num_samples):
        minutes.append(minute)
        values.append(area.total_resource_value)

        area.update()

        if verbose:
            print(minute, ":", values[-1])

    length, start = find_longest_common_subsequence(values, verbose)
    sequence = values[start:start+length]
    if verbose:
        print("Found sequence:", sequence)
        print("Verifying prediction...")

    for test in range(100):
        minute = num_samples + test
        expected = sequence[(minute - start) % length]
        actual = area.total_resource_value

        assert actual == expected

        area.update()

    return sequence[(1000000000 - start) % length]


def day18():
    """ Solution to day 18 """
    args = parse_args()

    text = read_input(18, args.debug)

    if args.num_video_frames > 0:
        area = Area(text, True)
        num_updates = args.num_video_frames
    else:
        area = Area(text)
        num_updates = 10

    print("Part 1")
    print(part1(area, num_updates, args.verbose))

    area.close()

    area = Area(text)
    print("Part 2")
    print(part2(area, 1000, args.verbose))


if __name__ == "__main__":
    day18()
