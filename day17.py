from collections import deque
import heapq
import itertools

import numpy as np

from utils import read_input, parse_args

SAND = ord('.')
CLAY = ord('#')
WATER = ord('~')
SPRING = ord('+')
WET_SAND = ord('|')


class Clay:
    def __init__(self, spec):
        parts = spec.split(',')
        if parts[0].startswith('x'):
            x = int(parts[0].strip()[2:])
            parts = parts[1].strip()[2:].split('..')
            self.start = (int(parts[0]), x)
            self.end = (int(parts[1]), x)
            self.horizontal = False
        elif parts[0].startswith('y'):
            y = int(parts[0].strip()[2:])
            parts = parts[1].strip()[2:].split('..')
            self.start = (y, int(parts[0]))
            self.end = (y, int(parts[1]))
            self.horizontal = True
        else:
            raise ValueError("Invalid line spec: " + spec)
        
        assert str(self) == spec
    
    def draw(self, ground, top, left):
        if self.horizontal:
            row, col0 = self.start
            row, col1 = self.end
            row -= top
            col0 -= left
            col1 -= left
            for col in range(col0, col1 + 1):
                ground[row, col] = CLAY
        else:
            row0, col = self.start
            row1, col = self.end
            row0 -= top
            row1 -= top
            col -= left
            for row in range(row0, row1 + 1):
                ground[row, col] = CLAY
    
    @property
    def extent(self):
        top, left = self.start
        bottom, right = self.end
        if self.horizontal:
            bottom += 1
        else:
            right += 1

        return top, left, bottom, right
    
    def __repr__(self):
        if self.horizontal:
            return "y={}, x={}..{}".format(self.start[0], self.start[1], self.end[1])
        
        return "x={}, y={}..{}".format(self.start[1], self.start[0], self.end[0])

class Ground:
    def __init__(self, clays):
        self.top, self.left, self.bottom, self.right = 0, 500, 0, 500
        for clay in clays[1:]:
            clay_top, clay_left, clay_bottom, clay_right = clay.extent
            if clay_top < self.top:
                self.top = clay_top
            
            if clay_left < self.left:
                self.left = clay_left
            
            if clay_bottom > self.bottom:
                self.bottom = clay_bottom
            
            if clay_right > self.right:
                self.right = clay_right
        
        self.left -= 1
        self.right += 1
        self.rows = self.bottom - self.top
        self.columns = self.right - self.left
        self._blocks = np.zeros((self.rows, self.columns), np.int32)
        self._blocks[:] = SAND
        self._blocks[0, 500 - self.left] = SPRING
        self._min_row = 1
        self._max_row = 3
        self._min_col = 499 - self.left
        self._max_col = 502 - self.left
        self._buffer = np.zeros_like(self._blocks)
        for clay in clays:
            clay.draw(self._blocks, self.top, self.left)

    def _is_drop(self, top):
        return top == WET_SAND
    
    def _is_flow_left(self, right, bottom_right):
        if right == WET_SAND:
            return bottom_right in (WATER, CLAY)
    
    def _is_flow_right(self, left, bottom_left):
        if left == WET_SAND:
            return bottom_left in (WATER, CLAY)
    
    def _tile_is_wet(self, row, col):
        tile = self._blocks[row, col]
        if tile == SAND:
            if self._is_drop(self._blocks[row-1, col]):
                return True

            if self._is_flow_left(self._blocks[row, col+1], self._blocks[row+1, col+1]):
                return True
            
            if self._is_flow_right(self._blocks[row, col-1], self._blocks[row+1, col-1]):
                return True
        
        return False
      
    def add_water(self):
        self._blocks[1 - self.top, 500 - self.left] = WET_SAND
        np.copyto(self._buffer, self._blocks)

        min_row = self._max_row
        min_col = self._max_col
        max_col = self._min_col
        max_row = self._min_row
        new_tiles = False
        for row in range(self._min_row, self._max_row):
            for col in range(self._min_col, self._max_col):
                if self._blocks[row, col] == WET_SAND:
                    min_col = col if col < min_col else min_col
                    max_col = col if col > max_col else max_col
                elif self._tile_is_wet(row, col):
                    new_tiles = True
                    min_row = row if row < min_row else min_row
                    max_row = row if row > max_row else max_row
                    min_col = col if col < min_col else min_col
                    max_col = col if col > max_col else max_col
                    self._buffer[row, col] = WET_SAND
        
        self._min_row = max(min_row - 2, 1)
        self._max_row = min(max_row + 2, self.rows-1)
        self._min_col = max(min_col - 2, 0)
        self._max_col = min(max_col + 2, self.columns)

        if self._max_row == self.rows - 1:
            for col in range(self.columns):
                if self._buffer[-1, col] == SAND:
                    if self._buffer[-2, col] == WET_SAND:
                        new_tiles = True
                        self._buffer[-1, col] = WET_SAND

        if not new_tiles:
            return False
              
        for row in reversed(range(self._min_row, self._max_row)):
            start = None
            for col in range(self.columns):
                tile = self._buffer[row, col]
                bottom = self._buffer[row+1, col]
                if tile == WET_SAND:
                    left = self._buffer[row, col-1]
                    if left == CLAY and bottom in (CLAY, WATER):
                        start = col
                elif tile == SAND:
                    start = None
                elif bottom not in (CLAY, WATER):
                    start = None
                elif tile == CLAY:
                    if start:
                        for basin_col in range(start, col):
                            self._buffer[row, basin_col] = WATER
                        
                        start = None
                
               
        self._blocks, self._buffer = self._buffer, self._blocks
        return True
    
    @property
    def active_region(self):
        return self._min_row, self._min_col, self._max_row, self._max_col

    @property    
    def reachable_tiles(self):
        return np.sum(self._blocks == WATER) + np.sum(self._blocks == WET_SAND)

    def __repr__(self):
        lines = [[chr(block) for block in row] for row in self._blocks]
        return "\n".join(["".join(line) for line in lines])    

def parse_input(lines):
    lines = deque(lines)
    clays = []
    while lines:
        line = lines.popleft().strip()
        if not line:
            break
        
        clays.append(Clay(line))
    
    return Ground(clays)
    

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
