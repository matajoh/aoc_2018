from collections import namedtuple

import numpy as np

from utils import read_input, parse_args, diff, PriorityQueue


class Point(namedtuple("Point", ("x, y, z"))):
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    @property
    def length(self):
        return self.x + self.y + self.z


class Nanobot(namedtuple("Nanobot", ("x", "y", "z", "radius", "cube"))):
    @staticmethod
    def parse(spec):
        # pos=<0,0,0>, r=4
        spec = spec.strip()
        pos_end = spec.index('>')
        pos = [int(part.strip()) for part in spec[5:pos_end].split(',')]
        rad_start = spec.index('=', pos_end)
        rad = int(spec[rad_start+1:].strip())
        cube = Cube(pos[0] - rad,
                    pos[0] + rad + 1,
                    pos[1] - rad,
                    pos[1] + rad + 1,
                    pos[2] - rad,
                    pos[2] + rad + 1)

        nanobot = Nanobot(pos[0], pos[1], pos[2], rad, cube)

        assert str(nanobot)[8:-1] == spec, diff(str(nanobot), spec)
        return nanobot

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
        if self.cube.intersects(cube):
            if cube.contains(self):
                return True

            for face in cube.faces():
                if self.intersects_plane(face):
                    return True

            return False

        return False

    def intersects_plane(self, plane):
        print(self, plane)
        # logic is much simpler due to aligned cube
        # find point of intersection
        # verify it is inside the plane
        distance = plane.a*self.x + plane.b*self.y + plane.c*self.z + plane.d
        print(distance*distance, plane.squared_mag, self.radius)
        return distance*distance <= plane.squared_mag*self.radius*self.radius


class Plane(namedtuple("Plane", ("a", "b", "c", "d"))):
    @staticmethod
    def from_points(A, B, C):
        A = np.array(A, np.int32)
        B = np.array(B, np.int32)
        C = np.array(C, np.int32)
        AB = B - A
        AC = C - A
        N = np.cross(AB, AC)
        a = N[0]
        b = N[1]
        c = N[2]
        d = -np.sum(N*C)
        plane = Plane(a, b, c, d)
        assert plane.contains(A)
        assert plane.contains(B)
        assert plane.contains(C)
        return plane

    @property
    def squared_mag(self):
        return self.a*self.a + self.b*self.b + self.c*self.c

    def contains(self, point):
        return self.a*point[0] + self.b*point[1] + self.c*point[2] + self.d == 0


class Cube(namedtuple("Cube", ("left", "right", "up", "down", "front", "back"))):
    def intersects(self, cube):
        return cube.left <= self.right and cube.right >= self.left and\
            cube.up <= self.down and cube.down >= self.up and \
            cube.front <= self.back and cube.back >= self.front

    def faces(self):
        x_values = [self.left, self.left, self.left,
                    self.right, self.right, self.right,
                    self.left, self.left, self.right,
                    self.left, self.left, self.right,
                    self.left, self.left, self.right,
                    self.left, self.left, self.right
                    ]
        y_values = [self.up, self.down, self.down,
                    self.up, self.down, self.down,
                    self.up, self.up, self.up,
                    self.down, self.down, self.down,
                    self.up, self.down, self.down,
                    self.up, self.down, self.down]
        z_values = [self.front, self.front, self.back,
                    self.front, self.front, self.back,
                    self.front, self.back, self.back,
                    self.front, self.back, self.back,
                    self.front, self.front, self.front,
                    self.back, self.back, self.back]
        corners = zip(x_values, y_values, z_values)
        corners = [Point(x, y, z) for x, y, z in corners]
        for i in range(6):
            yield Plane.from_points(corners[i*3], corners[i*3+1], corners[i*3+2])

    def parts(self):
        x = self.left + (self.width // 2)
        y = self.up + (self.height // 2)
        z = self.front + (self.depth // 2)

        lefts = [self.left, self.left, self.left, self.left, x, x, x, x]
        rights = [x, x, x, x, self.right, self.right, self.right, self.right]
        ups = [self.up, self.up, y, y, self.up, self.up, y, y]
        downs = [y, y, self.down, self.down, y, y, self.down, self.down]
        fronts = [self.front, z, self.front, z, self.front, z, self.front, z]
        backs = [z, self.back, z, self.back, z, self.back, z, self.back]

        for left, right, up, down, front, back in zip(lefts, rights, ups, downs, fronts, backs):
            yield Cube(left, right, up, down, front, back)

    def contains(self, point):
        return point.x >= self.left and point.x < self.right and \
            point.y >= self.up and point.y < self.down and \
            point.z >= self.front and point.z < self.back

    @property
    def size(self):
        return self.width * self.height * self.depth

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.down - self.up

    @property
    def depth(self):
        return self.back - self.front


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
    left = nanobots[0].x
    up = nanobots[0].y
    front = nanobots[0].z
    right, down, back = left, up, front

    for nanobot in nanobots[1:]:
        left = min(nanobot.x, left)
        up = min(nanobot.y, up)
        front = min(nanobot.z, front)
        right = max(nanobot.x, right)
        down = max(nanobot.y, down)
        back = max(nanobot.z, back)

    cube = Cube(left, right, up, down, front, back)
    num_bots = num_bots_for_cube(cube, nanobots)
    assert num_bots == len(nanobots)

    queue = PriorityQueue()
    queue.add(cube, -num_bots)

    while queue:
        priority, cube = queue.pop()
        print("looking at", cube)
        if cube.size == 0:
            continue

        if cube.size == 1:
            point = Point(cube.left, cube.up, cube.front)
            assert priority == num_bots_for_point(point, nanobots)
            return point
        else:
            for part in cube.parts():
                num_bots = num_bots_for_cube(part, nanobots)
                queue.add(part, -num_bots)


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
    cube = Cube(2, 6, -2, 4, -3, -1)
    faces = list(cube.faces())
    print(faces)

    bots = [
        (Nanobot.parse("pos=<4,1,-2>, r=4"), True), # inside
        (Nanobot.parse("pos=<0,1,-2>, r=4"), True), # left
        (Nanobot.parse("pos=<8,1,-2>, r=4"), True), # right
        (Nanobot.parse("pos=<4,-4,-2>, r=4"), True), # up
        (Nanobot.parse("pos=<4,6,-2>, r=4"), True), # down
        (Nanobot.parse("pos=<4,-5,-2>, r=4"), True), # front
        (Nanobot.parse("pos=<4,1,-2>, r=4"), True), # back
        (Nanobot.parse("pos=<0,-4,-4>, r=2"), False),
        (Nanobot.parse("pos=<0,-3,0>, r=2"), False),
        (Nanobot.parse("pos=<0,1,-4>, r=2"), False),
        (Nanobot.parse("pos=<0,1,0>, r=2"), False),
        (Nanobot.parse("pos=<8,-3,-4>, r=2"), False),
        (Nanobot.parse("pos=<8,-3,0>, r=2"), False),
        (Nanobot.parse("pos=<8,1,-4>, r=2"), False),
        (Nanobot.parse("pos=<8,1,0>, r=2"), False)
    ]

    for bot, expected in bots:
        actual = bot.intersects_cube(cube)
        assert actual == expected, "{} {}".format(bot, cube)


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
