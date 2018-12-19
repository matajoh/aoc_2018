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

Point = namedtuple('Point', ('row', 'col'))

DOWN = Point(1, 0)
LEFT = Point(0, -1)
RIGHT = Point(0, 1)

class Drop(namedtuple('Drop', ('row', 'col'))):
    def __init__(self, row, col, flowing, water):
        super().__init__(row, col)
        self._flowing = flowing
        self._water = water
        self._left = col
        self._right = col
        self._flowing.add(self)
    
    def __add__(self, other):
        return Drop(self.row + other.row, self.col + other.col, self._flowing, self._water)
    
    def _settle(self):
        for col in range(self._left, self._right+1):
            self._flowing.remove(Point(self.row, col))
            self._water.add(Point(self.row, col))
    
    @property
    def left(self):
        return self._left
    
    @left.setter
    def left(self, col):
        self._left = col
        if self._right:
            self._settle()

    @property
    def right(self):
        return self._right
    
    @right.setter
    def right(self, col):
        self._right = col
        if self._left:
            self._settle()
    
    def drop(self, clay, water):
        if self + DOWN in (clay | water):
            return Flow(self.row, self.col, self._flowing, True), Flow(self.row, self.col, self._flowing, False)

        return self + DOWN


class Flow(namedtuple('Flow', ('row', 'col'))):
    def __init__(self, row, col, left, drop):
        super().__init__(row, col)
        self._point = point
        self._left = left
        self._drop = drop
    
    def flow(self, clay):
        if self._left:
            if self + left in clay:
                
            self._point += LEFT
        else:
            self.point += RIGHT
        
        if self._point + LEFT in clay:
            self._drop.left = self._point
            return None
        
        self._point += LEFT
        return self._point
    


class Ground:
    def __init__(self, lines):
        pass
    
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
