from collections import deque
import heapq
import itertools

import numpy as np

from utils import read_input, parse_args

SAND = ord('.')
CLAY = ord('#')
WATER = ord('~')
SPRING = ord('+')
DRIED_SAND = ord('|')

class Drop:
    def __init__(self, pos, flow_left, index):
        row, col = pos
        self.pos = pos
        self.left = (row, col-1)
        self.right = (row, col+1)
        self.down = (row+1, col)
        self.flow_left = flow_left
        self.index = index
    
    def __lt__(self, other):
        return self.index < other.index
    
    def __repr__(self):
        return "Drop({}, flow_left={})".format(self.pos, self.flow_left)
    
    def drop(self):
        return Drop(self.down, None, self.index)
    
    def flow(self):
        if self.flow_left:
            return Drop(self.left, True, self.index)
        
        return Drop(self.right, False, self.index)
    
    def split(self):
        assert self.flow_left is None
        return [
            Drop(self.pos, True, self.index),
            Drop(self.pos, False, self.index)
        ]

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

        for clay in clays:
            clay.draw(self._blocks, self.top, self.left)

    def _find_left(self, pos, blocks):
        row, col = pos
        col -= 1
        while col >= 0:
            if self._blocks[row+1, col] in (SAND, DRIED_SAND):
                return None

            if self._blocks[row, col] in blocks:
                return col

            col -= 1
        
        return None

    def _find_right(self, pos, blocks):
        row, col = pos
        col += 1
        while col < self.columns:
            if self._blocks[row+1, col] in (SAND, DRIED_SAND):
                return None

            if self._blocks[row, col] in blocks:
                return col

            col += 1
        
        return None
      
    def add_water(self, report, verbose):
        spring = (0- self.top, 500 - self.left)
        counter = itertools.count()
        drops = []

        def add_spring():
            index = next(counter)
            num_water = np.sum(self._blocks == WATER)
            if index % report == 0:
                print("Drop", index, ":", num_water)
                if verbose:
                    print(self, "\n")

            heapq.heappush(drops, Drop(spring, None, index))

        add_spring()
        while drops:
            drop = heapq.heappop(drops)

            assert self._blocks[drop.pos] != SAND
            
            while drop.down[0] < self.rows:
                if self._blocks[drop.down] in (SAND, DRIED_SAND):
                    assert drop.flow_left is None
                    drop = drop.drop()
                    self._blocks[drop.pos] = DRIED_SAND
                else:
                    break
            
            if drop.down[0] == self.rows:
                continue

            # water or clay beneath
            if drop.flow_left is None:
                for flow in drop.split():
                    heapq.heappush(drops, flow)
            elif drop.flow_left:
                while drop.pos[0] >= 0:
                    if self._blocks[drop.down] in (SAND, DRIED_SAND):
                        heapq.heappush(drops, Drop(drop.pos, None, drop.index))
                        break
                    elif self._blocks[drop.left] in (SAND, DRIED_SAND):
                        drop = drop.flow()
                        self._blocks[drop.pos] = DRIED_SAND
                    else:
                        break

                if self._blocks[drop.down] in (SAND, DRIED_SAND):
                    continue

                assert self._blocks[drop.left] in (WATER, CLAY)
                rcol = self._find_right(drop.pos, (WATER, CLAY))
                if rcol:
                    row, col = drop.pos                            
                    while col < rcol:
                        self._blocks[row, col] = WATER
                        col += 1

                    add_spring()
                else:
                    continue
            else:
                while drop.pos[0] < self.columns:
                    if self._blocks[drop.down] in (SAND, DRIED_SAND):
                        heapq.heappush(drops, Drop(drop.pos, None, drop.index))
                        break
                    elif self._blocks[drop.right] in (SAND, DRIED_SAND):
                        drop = drop.flow()
                        self._blocks[drop.pos] = DRIED_SAND
                    else:
                        break

    @property    
    def reachable_tiles(self):
        return np.sum(self._blocks == WATER) + np.sum(self._blocks == DRIED_SAND)

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
    
    ground.add_water(5, args.verbose)
    if args.verbose:
        print(ground)
    
    print(ground)
    print("Part 1")
    print("Reachable tiles:", ground.reachable_tiles)

if __name__ == "__main__":
    day17()
