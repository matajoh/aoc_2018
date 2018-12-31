""" Solution to day 25 of the 2018 Advent of Code """

from collections import deque, namedtuple

import pytest
import numpy as np

from utils import read_input, parse_args, diff


class Point(namedtuple("Point", (("x", "y", "z", "t")))):
    """ Class representing a space/time position """

    def __sub__(self, other):
        distance = abs(other.x - self.x)
        distance += abs(other.y - self.y)
        distance += abs(other.z - self.z)
        distance += abs(other.t - self.t)

        return distance

    @staticmethod
    def parse(text):
        """ Parses a point from the line of text """
        parts = [int(part) for part in text.strip().split(',')]
        point = Point(*parts)
        actual = "{},{},{},{}".format(point.x, point.y, point.z, point.t)
        assert actual == text, diff(actual, text)
        return point


def parse_points(lines):
    """ Parse a list of points from the provided lines """
    lines = deque(lines)
    current = []
    while lines:
        line = lines.popleft().strip()
        if line:
            current.append(Point.parse(line))
        else:
            yield current
            current = []

    if current:
        yield current


THRESHOLD = 3


def build_constellation(edges, start, visited):
    """ Build a constellation of points """
    num_points = edges.shape[0]
    constellation = set()
    nodes = [start]
    while nodes:
        point = nodes.pop()
        visited.add(point)

        for other in range(num_points):
            if edges[point, other] and other not in constellation:
                constellation.add(other)
                nodes.append(other)

    return constellation


def count_constellations(points):
    """ Count the number of constellations in a list of points """

    num_points = len(points)
    edges = np.zeros((num_points, num_points), np.bool)
    for i in range(num_points):
        edges[i, i] = True
        point_i = points[i]
        for j in range(i+1, num_points):
            edges[i, j] = (point_i - points[j]) <= THRESHOLD
            edges[j, i] = edges[i, j]

    visited = set()
    constellations = []
    for i in range(num_points):
        if i in visited:
            continue

        constellations.append(build_constellation(edges, i, visited))

    return len(constellations)


def read_test_tuples():
    """ Read the test data """
    lines = read_input(25, True)
    point_sets = list(parse_points(lines))
    expected_counts = [4, 3, 8]

    return zip(point_sets, expected_counts)


TEST_TUPLES = list(read_test_tuples())


@pytest.mark.parametrize("point_set, expected", TEST_TUPLES)
def test_day25(point_set, expected):
    """ Test the solution """

    actual = count_constellations(point_set)
    assert actual == expected


def day25():
    """ Solution to day 25 """
    parse_args()
    lines = read_input(25)
    points = next(parse_points(lines))
    print("Part 1")
    print(count_constellations(points))


if __name__ == "__main__":
    day25()
