""" Solution to day 3 of the 2018 Advent of Code """

from collections import namedtuple
import re
import numpy as np
from utils import read_input, diff


PATTERN = (r"^#(?P<index>\d+) @ "
           r"(?P<left>\d+),(?P<top>\d+): "
           r"(?P<width>\d+)x(?P<height>\d+)$")


class Claim(namedtuple("Rect", ("index", "left", "top", "width", "height"))):
    """ Class encapsulating a rectangular claim """

    regex = re.compile(PATTERN)

    @staticmethod
    def parse(spec):
        """ Parse a Rect from the specification """
        match = Claim.regex.match(spec)
        claim = Claim(int(match.group("index")),
                      int(match.group("left")),
                      int(match.group("top")),
                      int(match.group("width")),
                      int(match.group("height")))
        assert str(claim) == spec, diff(str(claim), spec)
        return claim

    def __repr__(self):
        return "#{} @ {},{}: {}x{}".format(self.index, self.left,
                                           self.top, self.width, self.height)

    @property
    def right(self):
        """ The right edge """
        return self.left + self.width

    @property
    def bottom(self):
        """ The bottom edge """
        return self.top + self.height

    def draw(self, canvas):
        """ Draws the claim to the provided canvas """
        patch = canvas[self.top:self.bottom, self.left:self.right]
        canvas[self.top:self.bottom, self.left:self.right] = patch + 1

    def no_overlap(self, canvas):
        """ Tests for overlap with other claims """
        overlap_sum = np.sum(canvas[self.top:self.bottom, self.left:self.right])
        return overlap_sum == self.width*self.height


def find_non_overlapping_claim(canvas, claims):
    """ Find the claim which does not overlap any others """
    for claim in claims:
        if claim.no_overlap(canvas):
            return claim.index

    return None


def day3():
    """ Solution to day 3 """
    lines = read_input(3)
    claims = [Claim.parse(line) for line in lines]
    canvas = np.zeros((1000, 1000), np.int32)
    for claim in claims:
        claim.draw(canvas)

    print("Part 1")
    print(np.sum(canvas >= 2))
    print("Part 2")
    print(find_non_overlapping_claim(canvas, claims))


if __name__ == "__main__":
    day3()
