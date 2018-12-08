""" Solution to day 3 of the 2018 Advent of Code """

import numpy as np
from utils import read_input


class Rect:
    """ Class encapsulating a rectangle """

    def __init__(self, spec):
        parts = spec.split('@')
        self.id = parts[0][1:].strip() #pylint: disable=C0103

        parts = parts[1].split(':')
        left, top = parts[0].split(',')
        width, height = parts[1].split('x')
        self.left = int(left.strip())
        self.top = int(top.strip())
        self.width = int(width.strip())
        self.height = int(height.strip())

    @property
    def right(self):
        """ The right edge """
        return self.left + self.width

    @property
    def bottom(self):
        """ The bottom edge """
        return self.top + self.height

    def draw(self, canvas):
        """ Draws the rectangle to the provided canvas """
        for row in range(self.top, self.bottom):
            for col in range(self.left, self.right):
                canvas[row, col] += 1

    def no_overlap(self, canvas):
        """ Tests for overlap with other rectangles """
        overlap_sum = np.sum(canvas[self.top:self.bottom, self.left:self.right])
        return overlap_sum == self.width*self.height


def part1(canvas, claims):
    """ Solution to part 1 """
    for claim in claims:
        claim.draw(canvas)

    print(np.sum(canvas >= 2))


def part2(canvas, claims):
    """ Solution to part 2 """
    for claim in claims:
        if claim.no_overlap(canvas):
            print(claim.id)


def day3():
    """ Solution to day 3 """
    lines = read_input(3).split('\n')
    claims = [Rect(line) for line in lines]
    canvas = np.zeros((1000, 1000), np.int32)
    print("Part 1")
    part1(canvas, claims)
    print("Part 2")
    part2(canvas, claims)


if __name__ == "__main__":
    day3()
