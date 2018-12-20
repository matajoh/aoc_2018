""" Solution to day 20 of the 2018 Advent of Code """

from collections import deque

from utils import read_input, parse_args, Point

WALL = '#'
NS_DOOR = '-'
EW_DOOR = '|'
ROOM = '.'
START = 'X'

DIRS = {
    'N': Point(-1, 0),
    'E': Point(0, 1),
    'S': Point(1, 0),
    'W': Point(0, -1)
}


def read_debug_tuples():
    """ Read the debug input/output tuples """
    num_doors = [3, 10, 18, 23, 31]
    lines = deque([line.strip() for line in read_input(20, True).split('\n')])
    case = 0
    while lines:
        regex = lines.popleft()
        expected = []
        while lines:
            line = lines.popleft()
            if not line:
                break

            expected.append(line)

        yield regex, "\n".join(expected), num_doors[case]

        case += 1


def move_to(room, direction, rooms, doors):
    """ Move to the room, creating rooms and doors along the way """
    door = room + direction
    doors.add(door)
    room = door + direction
    rooms.add(room)
    return room


def create_complex(regex):
    """ Create the rooms and doors in the complex from the regex """
    tokens = deque(regex)
    start = Point(0, 0)
    rooms = set([start])
    doors = set()
    frontier = set([start])
    options = []
    temp = set([start])
    stack = []
    assert tokens.popleft() == '^'
    while tokens[0] != '$':
        token = tokens.popleft()
        if token in DIRS:
            temp.clear()
            for end in frontier:
                temp.add(move_to(end, DIRS[token], rooms, doors))

            frontier, temp = temp, frontier
        if token == '(':
            stack.append((frontier, options))
            frontier = set(stack[-1][0])
            options = []
        elif token == '|':
            options.append(frontier)
            frontier = set(stack[-1][0])
        elif token == ')':
            options.append(frontier)
            frontier = set()
            for option in options:
                frontier.update(option)

            _, options = stack.pop()

    assert tokens.popleft() == '$'

    return rooms, doors


def find_shortest_paths(doors):
    """ Find the shortest paths to all rooms """
    shortest_paths = {}
    frontier = [(Point(0, 0), set())]
    while frontier:
        room, opened = frontier.pop()
        if room not in shortest_paths:
            shortest_paths[room] = len(opened)

        if len(opened) < shortest_paths[room]:
            shortest_paths[room] = len(opened)

        for direction in DIRS.values():
            door = room + direction
            if door in doors and door not in opened:
                frontier.append((door + direction, opened | set([door])))

    return shortest_paths


def to_string(rooms, doors):
    """ Convert the rooms and doors to an ASCII representation """
    min_row = 0
    max_row = 0
    min_col = 0
    max_col = 0
    for room in rooms:
        min_row = min(min_row, room.row)
        min_col = min(min_col, room.col)
        max_row = max(max_row, room.row)
        max_col = max(max_col, room.col)

    min_row -= 1
    min_col -= 1
    max_row += 1
    max_col += 1
    rows = (max_row - min_row) + 1
    cols = (max_col - min_col) + 1

    lines = [[WALL for _ in range(cols)] for _ in range(rows)]
    for room in rooms:
        row = room.row - min_row
        col = room.col - min_col
        if room.row == room.col == 0:
            lines[row][col] = START
        else:
            lines[row][col] = ROOM

    for door in doors:
        row = door.row - min_row
        col = door.col - min_col
        if row % 2 == 0:
            lines[row][col] = NS_DOOR
        else:
            lines[row][col] = EW_DOOR

    return "\n".join(["".join(line) for line in lines])


def part1(doors):
    """ Compute the longest path to a room in the complex """
    max_length = 0
    frontier = [(Point(0, 0), set())]
    while frontier:
        room, opened = frontier.pop()
        if len(opened) > max_length:
            max_length = len(opened)

        for direction in DIRS.values():
            door = room + direction
            if door in doors and door not in opened:
                frontier.append((door + direction, opened | set([door])))

    return max_length


def debug_part1():
    """ Debug the part 1 solution """
    for regex, expected_repr, expected_doors in read_debug_tuples():
        rooms, doors = create_complex(regex)
        actual_repr = to_string(rooms, doors)
        assert actual_repr == expected_repr, "\n{}\n!=\n{}".format(
            actual_repr, expected_repr)
        actual_doors = part1(doors)
        assert actual_doors == expected_doors, "{} != {}".format(
            actual_doors, expected_doors)


def part2(doors):
    """ Compute the number of rooms with a shortest path >= 1000 """
    shortest_paths = find_shortest_paths(doors)
    num_rooms = 0
    for room in shortest_paths:
        if shortest_paths[room] >= 1000:
            num_rooms += 1

    return num_rooms


def day20():
    """ Solution to day 20 """
    args = parse_args()

    if args.debug:
        debug_part1()
    else:
        regex = read_input(20)
        rooms, doors = create_complex(regex)
        print("Part 1")
        print("Regex:", regex)
        num_doors = part1(doors)
        print("Furthest room requires passing", num_doors, "doors")
        print("\n" + to_string(rooms, doors))

        print("Part 2")
        print("Num rooms:", part2(doors))


if __name__ == "__main__":
    day20()
