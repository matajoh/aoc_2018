""" Solution to day 23 of the 2018 Advent of Code """

from collections import namedtuple

from utils import read_input, parse_args, diff, PriorityQueue


def range_dist(value, min_val, max_val):
    """ 0 if in the range, otherwise distance to the range """
    if value < min_val:
        return min_val - value

    if value > max_val:
        return value - max_val

    return 0


class Nanobot(namedtuple("Nanobot", ("x", "y", "z", "radius"))):
    """ Class representing a nanobot and its range """

    @staticmethod
    def parse(spec):
        """Parse a nanobot specification from the string"""
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
        """ The minimum value that is in range """
        return min(self.x - self.radius, self.y - self.radius, self.z - self.radius)

    @property
    def max(self):
        """ The maximum value that is in range """
        return max(self.x + self.radius, self.y + self.radius, self.z + self.radius)

    def __repr__(self):
        return "Nanobot(pos=<{},{},{}>, r={})".format(self.x, self.y,
                                                      self.z, self.radius)

    def __sub__(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)

    def in_range(self, other):
        """ Whether an entity is within range """
        return (self - other) <= self.radius

    def intersects_cube(self, cube):
        """ Whether this nanobot has any overlap with the cube """
        distance = range_dist(self.x, cube.x, cube.x + cube.length - 1)
        distance += range_dist(self.y, cube.y, cube.y + cube.length - 1)
        distance += range_dist(self.z, cube.z, cube.z + cube.length - 1)
        return distance <= self.radius


class Cube(namedtuple("Cube", ("x", "y", "z", "length"))):
    """ Class representing a cube in 3D space with equal sides """
    @property
    def distance(self):
        """ The distance from this cube to the origin """
        return abs(self.x) + abs(self.y) + abs(self.z)

    def parts(self):
        """ The 8 equal sub-cubes of this cube """
        length = self.length // 2
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    yield Cube(self.x + x*length, self.y+y*length, self.z + z*length, length)


def read_nanobots(lines):
    """ Read the list of nanobots from the provided lines """
    nanobots = []
    for line in lines:
        nanobots.append(Nanobot.parse(line))

    return nanobots


def find_strongest(nanobots):
    """ Find the strongest nanobots """
    nanobots.sort(key=lambda nanobot: nanobot.radius, reverse=True)
    max_radius = nanobots[0].radius
    strongest = []
    for nanobot in nanobots:
        if nanobot.radius == max_radius:
            strongest.append(nanobot)
        else:
            break

    return strongest


def count_in_range(strongest, nanobots, verbose):
    """ Counts the number of nanobots in range of the strongest nanobot """
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
    """ Counts the number of bots that overlap the cube """
    num_bots = 0
    for nanobot in nanobots:
        if nanobot.intersects_cube(cube):
            num_bots += 1

    return num_bots


def num_bots_for_point(point, nanobots):
    """ Returns the number of bots in range of a point """
    num_bots = 0
    for nanobot in nanobots:
        if nanobot.in_range(point):
            num_bots += 1

    return num_bots


def find_max_point(nanobots, verbose):
    """ Finds the maximum overlapping point """
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
        if verbose:
            print(cube, "length:", cube.length, "possible:", -priority[0])

        assert cube.length

        if cube.length == 1:
            num_bots = num_bots_for_point(cube, nanobots)
            assert - \
                priority[0] == num_bots, "{} != {}".format(-priority, num_bots)
            return cube

        for part in cube.parts():
            priority = (-num_bots_for_cube(part, nanobots), part.distance)
            queue.add(part, priority)


def debug(nanobots, verbose):
    """ Test for day 23 """
    strongest = find_strongest(nanobots)
    assert len(strongest) == 1
    strongest = strongest[0]
    assert strongest.radius == 4

    expected = 7
    actual = count_in_range(strongest, nanobots, verbose)

    assert actual == expected, "{} != {}".format(actual, expected)

    expected = Cube(1, 0, 0, 1)
    actual = find_max_point(nanobots, verbose)
    assert actual == expected, "{} != {}".format(actual, expected)

    assert actual.length == actual.x + actual.y + actual.z


def part1(nanobots, verbose):
    """ Solution to part 1 """
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
    """ Solution to part 2 """
    point = find_max_point(nanobots, verbose)
    return point.length


def day23():
    """ Solution to day 23 """
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
