from collections import deque, namedtuple
import heapq
import itertools

import numpy as np

from utils import read_input, parse_args

SAND = ord('.')
CLAY = ord('#')
WATER = ord('~')
SPRING = ord('+')
WET_SAND = ord('|')

class Point:
    def __init__(self, row, col):
        self._row = row
        self._col = col
        self._hash = (row, col).__hash__()
    
    def __eq__(self, other):
        return !(self.row != other.row or self.col != other.col)
    
    def __hash__(self):
        return self._hash
    
    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

DOWN = Point(1, 0)
LEFT = Point(0, -1)
RIGHT = Point(0, 1)


class Drop(Point):
    def __init__(self, row, col):
        super().__init__(row, col)
        self._left = None
        self._right = None
        self._flowed = False
    
    def __add__(self, other):
        return Drop(self.row + other.row, self.col + other.col)
       
    @property
    def left(self):
        return self._left
    
    @left.setter
    def left(self, col):
        self._left = col

    @property
    def right(self):
        return self._right
    
    @right.setter
    def right(self, col):
        self._right = col
    
    def flow(self, clay, water, flowing):
        flowing.add(self)
        down = self + DOWN
        if down in (clay | water):
            if self._flowed:
                if self._left and self._right:
                    for col in range(self._left, self._right + 1):
                        point = Point(self.row, col)
                        flowing.remove(point)
                        water.add(point)

                return None
            else:
                self._flowed = True
                return self, Flow(self.row, self.col, True, self), Flow(self.row, self.col, False, self)

        elif down not in flowing:
            return down
        
        return None


class Flow(Point):
    def __init__(self, row, col, flow_left, drop):
        super().__init__(row, col)
        self._flow_left = flow_left
        self._drop = drop
    
    def __add__(self, other):
        return Flow(self.row + other.row, self.col + other.col, self._flow_left, self._drop)

    def flow(self, clay, water, flowing):
        flowing.add(self)
        down = self + DOWN
        if self._flow_left:
            left = self + LEFT
            if left in clay:
                self._drop.left = self.col
                return None

            if down in (clay | water):
                return left
        else:
            right = self + RIGHT
            if right in clay:
                self._drop.right = self.col
                return None
            
            if down in (clay | water):
                return right            

        if down in flowing:
            return None
        
        return Drop(down.row, down.col)


def line_to_points(self, line):
    if line.startswith('x'):
        x=495, y=2..7
        parts = line.split(',')
        x = int(parts[0][2:])
        parts = parts[1][2:].split('..')
        y0 = int(parts[0])
        y1 = int(parts[1])
        for y in range(y0, y1 + 1):
            yield y, x
    
    if line.startswith('y'):
        pass
    
    raise ValueError("Invalid input: " + line)

        
class Ground:
    def __init__(self, lines):
        self._clay = set()
        self._water = set()
        self._flowing = set()
        for line in lines:


    def update(self):
        pass

def parse_input(lines):
    lines = deque(lines)
    while lines:
        line = lines.popleft().strip()
        if not line:
            break
        
    return "\n".join(lines)

def parse_repr(lines):
    lines = deque(lines)
    while lines:
        line = lines.popleft().strip()
        if not line:
            break
    
    text = []
    while lines:
        text.append(lines.popleft().strip())

    return "\n".join(text)

def day17():
    args = parse_args()
    lines = read_input(17, args.debug).split('\n')
    ground = parse_input(lines)
    if args.debug:
        actual = str(ground)
        expected = parse_repr(lines)
        assert actual == expected, "{}\n{}".format(actual, expected)
    
    iteration = 0
    while ground.add_water():
        iteration += 1
        if iteration % 5 == 0 and args.verbose:
            print(iteration, ":", ground.reachable_tiles, ground.active_region)
  
    with open("ground.txt", "w") as file:
        file.write(str(ground))
    
    print("Part 1")
    print("Reachable tiles:", ground.reachable_tiles)

if __name__ == "__main__":
    day17()
