""" Solution to day 10 of the 2018 Advent of Code """

import numpy as np
import matplotlib.pyplot as plt

from utils import read_input, parse_args

EXPECTED = [
    [1, 0, 0, 0, 1, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [1, 1, 1, 1, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 1, 1, 1]
]


def parse_pair(text):
    """ Parse a pair of numbers """
    parts = text.split(',')
    return int(parts[0].strip()), int(parts[1].strip())


def parse_line(line):
    """ Parse a line of input text """
    left = line.index('<') + 1
    right = line.index('>')
    col, row = parse_pair(line[left:right])

    left = line.index('<', right) + 1
    right = line.index('>', left)
    dcol, drow = parse_pair(line[left:right])

    return row, col, drow, dcol


def parse_input(lines):
    """ Parse the input and return the points and velocities """
    values = np.array([parse_line(line) for line in lines], np.int32)
    return values[:, :2], values[:, 2:]


class Rect:
    """ Class representing a rectangle """

    def __init__(self, left, top, right, bottom):
        self.left = int(left)
        self.top = int(top)
        self.width = int(right - left)
        self.height = int(bottom - top)

    @property
    def size(self):
        """ The size of the rectangle """
        return self.width * self.height

    @property
    def bottom(self):
        """ The bottom edge of the rectangle """
        return self.top + self.height

    @property
    def right(self):
        """ The right edge of the rectangle """
        return self.left + self.width

    def __repr__(self):
        return "(l={}, t={}, w={}, h={})".format(
            self.left,
            self.top,
            self.width,
            self.height
        )


def compute_bounding_box(points):
    """ Compute the bounding box that contains the provided points """
    min_row, min_col = np.min(points, axis=0)
    max_row, max_col = np.max(points, axis=0)
    return Rect(min_col, min_row, max_col + 1, max_row + 1)


def find_message(lines):
    """ Find the message that the points will eventually make """
    points, velocities = parse_input(lines)
    box = compute_bounding_box(points)

    size = box.size
    num_seconds = 0
    while True:
        points += velocities
        box = compute_bounding_box(points)
        if box.size > size:
            points -= velocities
            break

        size = box.size
        num_seconds += 1

    box = compute_bounding_box(points)
    canvas = np.zeros((box.height, box.width), np.bool)
    points = points - (box.top, box.left)
    canvas[points[:, 0], points[:, 1]] = True
    return canvas, num_seconds


def test_day10():
    """ Test for day 10 """
    lines = read_input(10, True)
    actual, num_seconds = find_message(lines)
    expected = np.array(EXPECTED, np.bool)
    np.testing.assert_array_equal(actual, expected)

    assert num_seconds == 3


def day10():
    """ Solution to day 10 """
    parse_args()

    lines = read_input(10)
    canvas, num_seconds = find_message(lines)
    print("Part 1")
    plt.imshow(canvas)
    plt.show()
    print("Part 2")
    print(num_seconds)


if __name__ == "__main__":
    day10()
