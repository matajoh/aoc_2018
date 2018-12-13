""" Solution to day 13 of the 2018 Advent of Code """

from collections import deque

import numpy as np

from utils import read_input, parse_args


NORTH_SOUTH = ord('|')
EAST_WEST = ord('-')
NE_CURVE = ord('/')
SW_CURVE = ord('/') + 1000
NW_CURVE = ord('\\')
SE_CURVE = ord('\\') + 1000
INTERSECTION = ord('+')
EMPTY = ord(' ')


def print_connections(connections):
    """ Print the connections around a track """
    lines = []
    for row in connections:
        lines.append([chr(spec) for spec in row])

    print("\n".join(["".join(line) for line in lines]))


VERTICAL_TRACKS = (INTERSECTION, NORTH_SOUTH)
HORIZONTAL_TRACKS = (INTERSECTION, EAST_WEST)


class Track:
    """ Class representing a piece of track """

    def __init__(self, connections):
        self.type = connections[1, 1]
        if self.type == NE_CURVE:
            vertical = VERTICAL_TRACKS + (NW_CURVE,)
            horizontal = HORIZONTAL_TRACKS + (NW_CURVE,)
            if connections[0, 1] in vertical and connections[1, 0] in horizontal:
                self.type = SW_CURVE
            else:
                assert connections[2, 1] in vertical
                assert connections[1, 2] in horizontal
        if self.type == NW_CURVE:
            vertical = VERTICAL_TRACKS + (NE_CURVE,)
            horizontal = HORIZONTAL_TRACKS + (NE_CURVE,)
            if connections[0, 1] in vertical and connections[1, 2] in horizontal:
                self.type = SE_CURVE
            else:
                assert connections[2, 1] in vertical
                assert connections[1, 0] in horizontal

    def __repr__(self):
        return chr(self.type % 1000)


NORTH = ord('^')
EAST = ord('>')
SOUTH = ord('v')
WEST = ord('<')

# left, straight, right
TURNS = [
    {
        NORTH: WEST,
        EAST: NORTH,
        SOUTH: EAST,
        WEST: SOUTH
    },
    {
        NORTH: NORTH,
        EAST: EAST,
        SOUTH: SOUTH,
        WEST: WEST
    },
    {
        NORTH: EAST,
        EAST: SOUTH,
        SOUTH: WEST,
        WEST: NORTH
    }
]


class Cart:
    """ Class representing a cart on the track """

    def __init__(self, tracks, direction, row, column):
        self.direction = direction
        self.tracks = tracks
        self.row = row
        self.col = column
        self.current = 0

    def __lt__(self, other):
        if self.row == other.row:
            return self.col < other.col

        return self.row < other.row

    def collides_with(self, other):
        """ Cpmputes whether this cart collides with the other """
        return self.row == other.row and self.col == other.col

    def move(self):
        """ Moves this cart along the track """
        if self.direction == NORTH:
            self.row -= 1
        elif self.direction == EAST:
            self.col += 1
        elif self.direction == SOUTH:
            self.row += 1
        elif self.direction == WEST:
            self.col -= 1
        else:
            raise ValueError("Invalid direction")

        track = self.tracks[self.row, self.col]
        if track.type == NE_CURVE:
            self._ne_turn()
        elif track.type == NW_CURVE:
            self._nw_turn()
        elif track.type == SE_CURVE:
            self._se_turn()
        elif track.type == SW_CURVE:
            self._sw_turn()
        elif track.type == INTERSECTION:
            self._intersection()
        else:
            if self.direction in (NORTH, SOUTH):
                assert track.type == NORTH_SOUTH
            elif self.direction in (WEST, EAST):
                assert track.type == EAST_WEST

    def _ne_turn(self):
        if self.direction == NORTH:
            self.direction = EAST
        elif self.direction == WEST:
            self.direction = SOUTH
        else:
            raise ValueError("Invalid direction at curve: " +
                             chr(self.direction))

    def _nw_turn(self):
        if self.direction == NORTH:
            self.direction = WEST
        elif self.direction == EAST:
            self.direction = SOUTH
        else:
            raise ValueError("Invalid direction at curve")

    def _se_turn(self):
        if self.direction == SOUTH:
            self.direction = EAST
        elif self.direction == WEST:
            self.direction = NORTH
        else:
            raise ValueError("Invalid direction at curve")

    def _sw_turn(self):
        if self.direction == SOUTH:
            self.direction = WEST
        elif self.direction == EAST:
            self.direction = NORTH
        else:
            raise ValueError("Invalid direction at curve")

    def _intersection(self):
        self.direction = TURNS[self.current][self.direction]
        self.current = (self.current + 1) % 3

    def __repr__(self):
        return chr(self.direction)


def parse_input(lines):
    """ Parses the input to create the tracks and carts """
    columns = len(lines[0])
    rows = len(lines)

    tracks = np.zeros((rows, columns), np.dtype(Track))
    track_spec = np.zeros((rows, columns), np.int32)
    carts = []
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            spec = ord(char)
            if spec in (NORTH, SOUTH):
                carts.append(Cart(tracks, spec, row, col))
                track_spec[row, col] = NORTH_SOUTH
            elif spec in (EAST, WEST):
                carts.append(Cart(tracks, spec, row, col))
                track_spec[row, col] = EAST_WEST
            else:
                track_spec[row, col] = spec

    track_spec = np.pad(track_spec, ((1, 1), (1, 1)),
                        'constant', constant_values=EMPTY)
    for row in range(rows):
        for col in range(columns):
            tracks[row, col] = Track(track_spec[row:row+3, col:col+3])

    return tracks, carts


def render_tracks(tracks, carts, collision):
    """ Renders the tracks and carts in ASCII """
    lines = []
    for track_row in tracks:
        lines.append([str(track) for track in track_row])

    for cart in carts:
        lines[cart.row][cart.col] = str(cart)

    if collision:
        lines[collision[1]][collision[0]] = 'X'

    return "\n".join(["".join(line) for line in lines])


def do_tick(carts, stop_on_collision):
    """ Performs a tick """
    in_queue = deque(carts)
    carts.clear()

    while in_queue:
        cart = in_queue.popleft()
        cart.move()
        collided = None
        for other in in_queue:
            if cart.collides_with(other):
                if stop_on_collision:
                    return cart.col, cart.row
                else:
                    collided = other
                    break

        if collided:
            in_queue.remove(collided)
            continue

        for other in carts:
            if cart.collides_with(other):
                if stop_on_collision:
                    return cart.col, cart.row
                else:
                    collided = other
                    break

        if collided:
            carts.remove(collided)
            continue

        carts.append(cart)

    carts.sort()
    return None


def part1(tracks, carts, verbose):
    """ Solution to part 1 """
    tick = 0
    carts.sort()
    if verbose:
        print("Start:", tick)
        print(render_tracks(tracks, carts, None))

    while True:
        collision = do_tick(carts, True)

        tick += 1

        if verbose:
            print("Tick:", tick)
            print(render_tracks(tracks, carts, collision))

        if collision:
            break

    print("Collision at: {},{}".format(collision[0], collision[1]))


def part2(tracks, carts, verbose):
    """ Solution to part 2 """
    tick = 0
    carts.sort()
    if verbose:
        print("Start:", tick)
        print(render_tracks(tracks, carts, None))

    while len(carts) > 1:
        do_tick(carts, False)

        tick += 1

        if verbose:
            print("Tick:", tick)
            print(render_tracks(tracks, carts, None))

    print("Final cart location: {},{}".format(carts[0].col, carts[0].row))


def day13():
    """ Solution to day 13 """
    args = parse_args()

    input_text = read_input(13, args.debug)
    tracks, carts = parse_input(input_text.split("\n"))
    render = render_tracks(tracks, carts, None)
    assert render == input_text

    print("Part 1")
    part1(tracks, carts, args.verbose)

    input_text = read_input(13, args.debug)
    tracks, carts = parse_input(input_text.split("\n"))
    render = render_tracks(tracks, carts, None)
    assert render == input_text

    print("Part 2")
    part2(tracks, carts, args.verbose)


if __name__ == "__main__":
    day13()
