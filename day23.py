from collections import namedtuple

import numpy as np

from utils import read_input, parse_args, diff

class Point(namedtuple("Point", ("x, y, z"))):
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)
    
    @property
    def length(self):
        return self.x + self.y + self.z

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
        assert str(nanobot) == spec, diff(str(nanobot), spec)
        return nanobot               
    
    @property
    def min_point(self):
        diff = self.radius // 3
        return Point(self.x - diff, self.y - diff, self - self.radius + 2*diff)
    
    def __repr__(self):
        return "pos=<{},{},{}>, r={}".format(self.x, self.y,
                                            self.z, self.radius)
    
    def __sub__(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)
    
    def in_range(self, other):
        return (self - other) <= self.radius
    
    def intersects(self, other):
        return (other - self) <= (self.radius + other.radius)
    
    @property
    def cube(self):
        return Cube(self.x - self.radius,
                    self.x + self.radius + 1,
                    self.y - self.radius,
                    self.y + self.radius + 1,
                    self.z - self.radius,
                    self.z + self.radius + 1)

class Cube(namedtuple("Cube", ("left", "right", "up", "down", "front", "back"))):
    def intersect_with(self, other):
        return Cube(
            max(self.left, other.left),
            min(self.right, other.right),
            max(self.up, other.up),
            min(self.down, other.down),
            max(self.front, other.front),
            min(self.back, other.back))
    
    def contains(self, other):
        return other.left <= self.right and\
               other.right >= self.left and\
               other.up <= self.down and\
               other.down >= self.up and\
               other.front <= self.back and\
               other.back >= self.front
    
    def points(self):
        num_points = (self.right - self.left) * (self.down - self.up) * (self.back - self.front)
        print("enumerating", num_points, "points")
        for x in range(self.left, self.right):
            for y in range(self.up, self.down):
                for z in range(self.front, self.back):
                    yield namedtuple("Point", ("x", "y", "z"))(x, y, z)
    
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

class MaxClique:
    def __init__(self, edges, verbose):
        self._edges = edges
        self._current = []
        self._max = []
        self._max_size = 0
        self._verbose = verbose
    
    def _find_color_groups(self, nodes):
        color_groups = []
        for node in nodes:
            adjacent = True
            for color_group in color_groups:
                if np.sum(self._edges[node][color_group]) == 0:           
                    color_group.append(node)
                    adjacent = False
                    break
            
            if adjacent:
                color_groups.append([node])

        return color_groups
    
    def _color_graph(self, nodes):
        if self._verbose:
            print("coloring graph of size", len(nodes))

        color_groups = self._find_color_groups(nodes)        
        nodes = []
        colors = []
        for color, color_group in enumerate(color_groups):
            nodes.extend(color_group)
            colors.extend([color + 1] * len(color_group))
        
        return nodes, colors
    
    def _color_greedy(self, color_groups, group):
        cliques = []
        if group == 0:
            for node in color_groups[0]:
                cliques.append([node])
        else:
            for node in color_groups[group]:
                possible_cliques = self._color_greedy(color_groups, group - 1)
                for clique in possible_cliques:
                    if np.prod(self._edges[node][clique]):
                        cliques.append(clique + [node])
        
        return cliques
    
    def find(self):
        nodes = list(range(self._edges.shape[0]))

        if self._verbose:
            print("Coloring nodes")
        color_groups = self._find_color_groups(nodes)

        if self._verbose:
            print("Finding maximum cliques")

        cliques = self._color_greedy(color_groups, len(color_groups) - 1)
        return cliques
        
        #self._max_clique(nodes)
        #return self._max

    def _max_clique(self, nodes):
        if self._verbose:
            print("finding max clique for graph of size", len(nodes))

        nodes, colors = self._color_graph(nodes)

        while nodes:
            node = nodes.pop()
            color = colors.pop()
            print("|Q| + C = ", len(self._current) + color, "|Qmax| = ", self._max_size)
            if len(self._current) + color >= self._max_size:
                self._current.append(node)
                adjacent = []
                for other in nodes:
                    if self._edges[node, other]:
                        adjacent.append(other)
                
                if adjacent:
                    self._max_clique(adjacent)
                elif len(self._current) > self._max_size:
                    self._max_size = len(self._current)
                    self._max = [self._current.copy()]
                elif len(self._current) == self._max_size:
                    self._max.append(self._current.copy())
                
                assert self._current.pop() == node
            else:
                return

def find_intersecting_groups(nanobots, verbose):
    num_bots = len(nanobots)
    edges = np.zeros((num_bots, num_bots), np.bool)
    for i in range(num_bots):
        edges[i, i] = True
        nanobot = nanobots[i]
        if verbose:
            print("checking", nanobot)

        for j in range(i + 1, num_bots):
            if nanobot.intersects(nanobots[j]):
                edges[i, j] = True
                edges[j, i] = True
    
    lookup = np.zeros(num_bots, np.dtype(Nanobot))
    lookup[:] = nanobots
    max_clique = MaxClique(edges, verbose)
    groups = max_clique.find()
    for group in groups:
        yield lookup[group]

def find_nearest_group_point(group, verbose):
    # compress group
    num_bots = len(group)
    contains = np.zeros((num_bots, num_bots), np.bool)
    for i in range(num_bots):
        for j in range(i+1, num_bots):
            if i == j:
                contains[i, j] = True
            else:
                contains[i, j] = group[i].contains(group[j])

    to_remove = []
    for i in range(num_bots):
        if np.prod(contains)
    pass

def find_nearest_point(groups, verbose):
    min_point = None
    for group in groups:
        point = find_nearest_group_point(group, verbose)
        if min_point is None:
            min_point = point
        elif point.length < min_point.length:
            min_point = point
    
    return min_point

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

    expected = 9
    groups = list(find_intersecting_groups(nanobots, verbose))

    group = groups[0]
    for lhs in group:
        for rhs in group:
            assert lhs.intersects(rhs), "{} does not intersect {}".format(lhs, rhs)
    
    print(group)
    expected = 3
    actual = len(group)
    assert actual == expected, "{} != {}".format(actual, expected)

    expected = exhaustive_point_search(nanobots)
    actual = find_nearest_point(groups, verbose)
    assert actual == expected, "{} != {}".format(actual, expected)


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
    groups = find_intersecting_groups(nanobots, verbose)
    point = find_nearest_point(groups, verbose)
    return point.x + point.y + point.z


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
