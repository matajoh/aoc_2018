from collections import namedtuple

import numpy as np

from utils import read_input, parse_args, diff, PriorityQueue


class Point(namedtuple("Point", ("x, y, z"))):
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    @property
    def length(self):
        return self.x + self.y + self.z

def range_dist(value, range):
    if value < range[0]:
        return range[0] - value
    
    if value > range[1]:
        return value - range[1]
    
    return 0


class Nanobot(namedtuple("Nanobot", ("x", "y", "z", "radius"))):
    @staticmethod
    def parse(spec):
        # pos=<0,0,0>, r=4
        spec = spec.strip()
        pos_end = spec.index('>')
        pos = [int(part.strip()) for part in spec[5:pos_end].split(',')]
        rad_start = spec.index('=', pos_end)
        rad = int(spec[rad_start+1:].strip())
        nanobot = Nanobot(pos[0], pos[1], pos[2], rad)

        assert str(nanobot)[8:-1] == spec, diff(str(nanobot), spec)
        return nanobot
    
    @property
    def min(self):
        return min(self.x - self.radius, self.y - self.radius, self.z - self.radius)
    
    @property
    def max(self):
        return max(self.x + self.radius, self.y + self.radius, self.z + self.radius)

    def __repr__(self):
        return "Nanobot(pos=<{},{},{}>, r={})".format(self.x, self.y,
                                                      self.z, self.radius)

    def __sub__(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)

    def in_range(self, other):
        return (self - other) <= self.radius

    def intersects_bot(self, bot):
        return (bot - self) <= (self.radius + bot.radius)

    def intersects_cube(self, cube):
        x_range = (cube.x, cube.x + cube.length - 1)
        y_range = (cube.y, cube.y + cube.length - 1)
        z_range = (cube.z, cube.z + cube.length - 1)
        distance = range_dist(self.x, x_range)
        distance += range_dist(self.y, y_range)
        distance += range_dist(self.z, z_range)
        return distance <= self.radius


class Cube(namedtuple("Cube", ("x", "y", "z", "length"))):
    @property
    def distance(self):
        return abs(self.x) + abs(self.y) + abs(self.z)

    def parts(self):
        length = self.length // 2
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    yield Cube(self.x + x*length, self.y+y*length, self.z + z*length, length)


def read_nanobots(lines):
    nanobots = []
    for line in lines:
        nanobots.append(Nanobot.parse(line))

    return nanobots


def find_strongest(nanobots):
    nanobots.sort(key=lambda nanobot: nanobot.radius, reverse=True)
    max_radius = nanobots[0].radius
    strongest = []
    for nanobot in nanobots:
        if nanobot.radius == max_radius:
            strongest.append(nanobot)

    return strongest


def count_in_range(strongest, nanobots, verbose):
    num_in_range = 0
    for nanobot in nanobots:
        in_range = strongest.in_range(nanobot)
        if verbose:
            print(
                "The nanoboat at",
                "{},{},{}".format(nanobot.x, nanobot.y, nanobot.z),
                "is distance",
                nanobot - strongest,
                "away, and so it is",
                "in range" if in_range else "not in range"
            )
        if in_range:
            num_in_range += 1

    return num_in_range


def num_bots_for_cube(cube, nanobots):
    num_bots = 0
    for nanobot in nanobots:
        if nanobot.intersects_cube(cube):
            num_bots += 1

    return num_bots

def num_bots_for_point(point, nanobots):
    num_bots = 0
    for nanobot in nanobots:
        if nanobot.in_range(point):
            num_bots += 1
    
    return num_bots


def find_max_point(nanobots, verbose):
    min_dim = nanobots[0].min
    max_dim = min_dim

    for nanobot in nanobots[1:]:
        min_dim = min(nanobot.min, min_dim)
        max_dim = max(nanobot.max, max_dim)

    size = max_dim - min_dim
    target_size = 1
    while target_size < size:
        target_size *= 2
    
    cube = Cube(min_dim, min_dim, min_dim, target_size)
    num_bots = num_bots_for_cube(cube, nanobots)
    assert num_bots == len(nanobots)

    queue = PriorityQueue()
    queue.add(cube, (-num_bots, cube.distance))

    while queue:
        priority, cube = queue.pop()
        print(cube, "length:", cube.length, "possible:", -priority[0])
        assert cube.length

        if cube.length == 1:
            num_bots = num_bots_for_point(cube, nanobots)
            assert -priority[0] == num_bots, "{} != {}".format(-priority, num_bots)
            return Point(cube.x, cube.y, cube.z)
        else:
            for part in cube.parts():
                priority = (-num_bots_for_cube(part, nanobots), part.distance)
                queue.add(part, priority)


def exhaustive_point_search(nanobots):
    min_vals = [100, 100, 100]
    max_vals = [-100, -100, -100]
    for nanobot in nanobots:
        min_vals[0] = min(min_vals[0], nanobot.x - nanobot.radius)
        min_vals[1] = min(min_vals[1], nanobot.y - nanobot.radius)
        min_vals[2] = min(min_vals[2], nanobot.z - nanobot.radius)

        max_vals[0] = max(max_vals[0], nanobot.x + nanobot.radius)
        max_vals[1] = max(max_vals[1], nanobot.y + nanobot.radius)
        max_vals[2] = max(max_vals[2], nanobot.z + nanobot.radius)

    max_bots = 0
    max_points = []
    for x in range(min_vals[0], max_vals[0] + 1):
        for y in range(min_vals[1], max_vals[1] + 1):
            for z in range(min_vals[2], max_vals[2] + 1):
                point = namedtuple("Point", ("x", "y", "z"))(x, y, z)
                num_bots = 0
                in_range = []
                for nanobot in nanobots:
                    if nanobot.in_range(point):
                        in_range.append(nanobot)
                        num_bots += 1

                if num_bots > max_bots:
                    max_bots = num_bots
                    max_points = [point]
                elif num_bots == max_bots:
                    max_points.append(point)

    return sorted(max_points, key=lambda point: point.x + point.y + point.z)[0]


def debug(nanobots, verbose):
    strongest = find_strongest(nanobots)
    assert len(strongest) == 1
    strongest = strongest[0]
    assert strongest.radius == 4

    expected = 7
    actual = count_in_range(strongest, nanobots, verbose)

    assert actual == expected, "{} != {}".format(actual, expected)

    expected = exhaustive_point_search(nanobots)
    actual = find_max_point(nanobots, verbose)
    assert actual == expected, "{} != {}".format(actual, expected)

    assert actual.length == actual.x + actual.y + actual.z


def part1(nanobots, verbose):
    strongest_bots = find_strongest(nanobots)
    if verbose:
        print("found strongest:", strongest_bots)

    max_in_range = 0
    for strongest in strongest_bots:
        num_in_range = count_in_range(strongest, nanobots, verbose)
        if num_in_range > max_in_range:
            max_in_range = num_in_range

    return max_in_range


def part2(nanobots, verbose):
    point = find_max_point(nanobots, verbose)
    return point.length


def day23():
    args = parse_args()

    lines = read_input(23, args.debug).split('\n')
    nanobots = read_nanobots(lines)

    if args.debug:
        debug(nanobots, args.verbose)
    else:
        print("Part 1")
        print(part1(nanobots, args.verbose))

        print("Part 2")
        print(part2(nanobots, args.verbose))


if __name__ == "__main__":
    day23()
