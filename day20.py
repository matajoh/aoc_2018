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

def parse_regex(tokens):
    paths = []
    path = []
    assert tokens.popleft() in ('^', '(')
    while tokens[0] not in ('$', ')'):
        token = tokens[0]
        if token == '(':
            options = parse_regex(tokens)
            for option in options:
                paths.append(path + option)
        elif token == '|':
            tokens.popleft()
            paths.append(path)
            path = []
        elif token in DIRS:
            tokens.popleft()
            path.append(token)
    
    assert tokens.popleft() in (')', '$')
    paths.append(path)
    return paths

def create_complex(regex):
    start = Point(0, 0)
    rooms = set([start])
    doors = set()
    paths = parse_regex(deque(regex))
    for path in paths:
        room = start
        for direction in path:
            door = room + DIRS[direction]
            doors.add(door)
            room = door + DIRS[direction]
            rooms.add(room)

    return rooms, doors

def walk_rooms(room, rooms, doors, opened):
    max_length = len(opened)
    for direction in DIRS.values():
        door = room + direction
        if door in doors and door not in opened:
            opened.add(door)
            length = walk_rooms(door + direction, rooms, doors, opened)
            if length > max_length:
                max_length = length
            
            opened.remove(door)
    
    return max_length

def to_string(rooms, doors):
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
        if row%2 == 0:
            lines[row][col] = NS_DOOR
        else:
            lines[row][col] = EW_DOOR
    
    return "\n".join(["".join(line) for line in lines])

def part1(regex):
    rooms, doors = create_complex(regex)
    num_doors = walk_rooms(Point(0, 0), rooms, doors, set())

    return to_string(rooms, doors), num_doors

def debug_part1():
    for regex, expected_repr, expected_doors in read_debug_tuples():
        actual_repr, actual_doors = part1(regex)
        assert actual_repr == expected_repr, "\n{}\n!=\n{}".format(actual_repr, expected_repr)
        assert actual_doors == expected_doors, "{} != {}".format(actual_doors, expected_doors)


def day20():
    args = parse_args()

    if args.debug:
        debug_part1()
    else:
        regex = read_input(20)
        print("Part 1")
        print("Regex:", regex)
        repr, num_doors = part1(regex)
        print("Furthest room requires passing", num_doors, "doors")
        print("\n" + repr)

if __name__ == "__main__":
    day20()
