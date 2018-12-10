""" Solution to day 10 of the 2018 Advent of Code """

import numpy as np
import matplotlib.pyplot as plt

from utils import read_input, parse_args


def parse_pair(text):
    """ Parse a pair of numbers """
    parts = text.split(',')
    return int(parts[0].strip()), int(parts[1].strip())


class Point:
    """ Class representing a moving point """

    def __init__(self, line):
        left = line.index('<') + 1
        right = line.index('>')
        self.col, self.row = parse_pair(line[left:right])

        left = line.index('<', right) + 1
        right = line.index('>', left)
        self.dcol, self.drow = parse_pair(line[left:right])

    def move(self, multiplier=1):
        """ Moves the point """
        self.row += self.drow*multiplier
        self.col += self.dcol*multiplier

    def __repr__(self):
        return "({}, {}) @ ({}, {})".format(self.col, self.row,
                                            self.dcol, self.drow)


class Rect:
    """ Class representing a rectangle """

    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.width = right - left
        self.height = bottom - top

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
    min_row, min_col = points[0].row, points[0].col
    max_row, max_col = min_row, min_col

    for point in points:
        min_row = min((min_row, point.row))
        min_col = min((min_col, point.col))
        max_row = max((max_row, point.row))
        max_col = max((max_col, point.col))

    return Rect(min_col, min_row, max_col + 1, max_row + 1)


def day10():
    """ Solution to day 10 """
    args = parse_args()

    if args.debug:
        lines = read_input(10, True).split('\n')
        rollout = 10
    else:
        lines = read_input(10).split("\n")
        rollout = 15000

    points = [Point(line) for line in lines]
    box = compute_bounding_box(points)
    size = box.size
    for second in range(rollout):
        for point in points:
            point.move()

        box = compute_bounding_box(points)
        if box.size > size:
            for point in points:
                point.move(-1)

            print("Took", second, "seconds")
            break
        else:
            size = box.size

    box = compute_bounding_box(points)
    canvas = np.zeros((box.height, box.width), np.bool)
    for point in points:
        row = point.row - box.top
        col = point.col - box.left
        canvas[row, col] = True

    plt.imshow(canvas)
    plt.show()


if __name__ == "__main__":
    day10()
