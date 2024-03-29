""" Solution to day 13 of the 2018 Advent of Code """

from collections import deque
import logging

import numpy as np

from utils import read_input, parse_args, ASCIIVideoBuilder


TRACK_MOD = 1000
NORTH_SOUTH = ord('|')
EAST_WEST = ord('-')
NE_CURVE = ord('/')
SW_CURVE = ord('/') + TRACK_MOD
NW_CURVE = ord('\\')
SE_CURVE = ord('\\') + TRACK_MOD
INTERSECTION = ord('+')
EMPTY = ord(' ')
NORTH = ord('^')
EAST = ord('>')
SOUTH = ord('v')
WEST = ord('<')
COLLISION = ord('X')


COLOR_MAP = {
    EMPTY: (0, 0, 0),
    NORTH_SOUTH: (0, 255, 0),
    EAST_WEST: (0, 255, 0),
    NE_CURVE: (0, 255, 0),
    NW_CURVE: (0, 255, 0),
    INTERSECTION: (0, 255, 0),
    NORTH: (255, 255, 255),
    EAST: (255, 255, 255),
    SOUTH: (255, 255, 255),
    WEST: (255, 255, 255),
    COLLISION: (255, 0, 0),
}


def print_connections(connections):
    """ Print the connections around a track """
    lines = []
    for row in connections:
        lines.append([chr(spec) for spec in row])

    print("\n".join(["".join(line) for line in lines]))


VERTICAL_TRACKS = (INTERSECTION, NORTH_SOUTH)
HORIZONTAL_TRACKS = (INTERSECTION, EAST_WEST)

def determine_track(connections):
    """ Determine the correct track type based on the connections """
    track = connections[1, 1]
    if track == NE_CURVE:
        vertical = VERTICAL_TRACKS + (NW_CURVE,)
        horizontal = HORIZONTAL_TRACKS + (NW_CURVE,)
        if connections[0, 1] in vertical and connections[1, 0] in horizontal:
            track = SW_CURVE
        else:
            assert connections[2, 1] in vertical
            assert connections[1, 2] in horizontal

    elif track == NW_CURVE:
        vertical = VERTICAL_TRACKS + (NE_CURVE,)
        horizontal = HORIZONTAL_TRACKS + (NE_CURVE,)
        if connections[0, 1] in vertical and connections[1, 2] in horizontal:
            track = SE_CURVE
        else:
            assert connections[2, 1] in vertical
            assert connections[1, 0] in horizontal

    return track


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
        if track == NE_CURVE:
            self._ne_turn()
        elif track == NW_CURVE:
            self._nw_turn()
        elif track == SE_CURVE:
            self._se_turn()
        elif track == SW_CURVE:
            self._sw_turn()
        elif track == INTERSECTION:
            self._intersection()
        else:
            if self.direction in (NORTH, SOUTH):
                assert track == NORTH_SOUTH
            elif self.direction in (WEST, EAST):
                assert track == EAST_WEST

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

    tracks = np.zeros((rows, columns), np.int32)
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
            tracks[row, col] = determine_track(track_spec[row:row+3, col:col+3])

    return tracks, carts


def update_state(state, tracks, carts, collision):
    """ Update the state of the simulation """
    state[:] = tracks % TRACK_MOD

    for cart in carts:
        state[cart.row, cart.col] = cart.direction

    if collision:
        state[collision[1], collision[0]] = ord('X')


def render_tracks(tracks, carts, collision):
    """ Renders the tracks and carts in ASCII """
    lines = []
    for track_row in tracks:
        lines.append([chr(track % TRACK_MOD) for track in track_row])

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

                collided = other
                break

        if collided:
            in_queue.remove(collided)
            continue

        for other in carts:
            if cart.collides_with(other):
                if stop_on_collision:
                    return cart.col, cart.row

                collided = other
                break

        if collided:
            carts.remove(collided)
            continue

        carts.append(cart)

    carts.sort()
    return None


def find_first_collision(tracks, carts, build_video):
    """ Find the first collision """

    if build_video:
        state = np.zeros(tracks.shape, np.uint8)
        builder = ASCIIVideoBuilder("day13.mp4", state, COLOR_MAP)
        update_state(state, tracks, carts, None)
        builder.add_frame(state)
    else:
        builder = None
        state = None

    tick = 0
    carts.sort()
    logging.debug("Start: %d", tick)
    if logging.DEBUG >= logging.root.level:
        logging.debug("%s", render_tracks(tracks, carts, None))

    while True:
        collision = do_tick(carts, True)

        tick += 1

        logging.debug("Tick: %d", tick)
        if logging.DEBUG >= logging.root.level:
            logging.debug(render_tracks(tracks, carts, collision))

        if builder:
            update_state(state, tracks, carts, collision)
            builder.add_frame(state)

        if collision:
            break

    if builder:
        builder.close()

    return collision[0], collision[1]


def find_last_surviving_cart(tracks, carts):
    """ Find the last surviving cart """
    tick = 0
    carts.sort()
    logging.debug("Start: %d", tick)
    if logging.DEBUG >= logging.root.level:
        logging.debug(render_tracks(tracks, carts, None))

    while len(carts) > 1:
        do_tick(carts, False)

        tick += 1

        logging.debug("Tick: %d", tick)
        if logging.DEBUG >= logging.root.level:
            logging.debug(render_tracks(tracks, carts, None))

    return carts[0].col, carts[0].row


def test_day13():
    """ Test for day 13 """

    input_text = read_input(13, True, no_split=True)
    tracks, carts = parse_input(input_text.split("\n"))
    render = render_tracks(tracks, carts, None)
    assert render == input_text

    expected = (2, 0)
    actual = find_first_collision(tracks, carts, False)
    assert actual == expected

    tracks, carts = parse_input(input_text.split("\n"))

    expected = (6, 4)
    actual = find_last_surviving_cart(tracks, carts)
    assert actual == expected


def day13():
    """ Solution to day 13 """
    args = parse_args()

    input_text = read_input(13, no_split=True)
    tracks, carts = parse_input(input_text.split("\n"))

    print("Part 1")
    print(find_first_collision(tracks, carts, args.video))

    tracks, carts = parse_input(input_text.split("\n"))

    print("Part 2")
    print(find_last_surviving_cart(tracks, carts))


if __name__ == "__main__":
    day13()
