from collections import deque, namedtuple

import numpy as np

from utils import read_input, parse_args, diff

class Point(namedtuple("Point", (("x", "y", "z", "t")))):
    def __sub__(self, other):
        return abs(other.x - self.x) + abs(other.y - self.y) + abs(other.z - self.z) + abs(other.t - self.t)

    @staticmethod
    def parse(text):
        parts = [int(part) for part in text.strip().split(',')]
        point = Point(*parts)
        actual = "{},{},{},{}".format(point.x, point.y, point.z, point.t)
        assert actual == text, diff(actual, text)
        return point


def parse_points(lines):
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

def debug():
    lines = read_input(25, True).split('\n')
    point_sets = list(parse_points(lines))
    expected_counts = [4, 3, 8]

    for point_set, expected in zip(point_sets, expected_counts):
        actual = count_constellations(point_set)
        assert actual == expected, "{} != {}".format(actual, expected)

def day25():
    args = parse_args()
    if args.debug:
        debug()
    else:
        lines = read_input(25).split("\n")
        points = next(parse_points(lines))
        print("Part 1")
        print(count_constellations(points))


if __name__ == "__main__":
    day25()
