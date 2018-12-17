from collections import deque

import numpy as np

from utils import read_input, parse_args

SAND = ord('.')
CLAY = ord('#')
WATER = ord('~')
SPRING = ord('+')
DRIED_SAND = ord('|')

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
    
    def _find_left(self, row, col, blocks):
        col -= 1
        print("Looking for", [chr(block) for block in blocks], "to the left of", col)
        while col >= 0:
            if self._blocks[row, col] in blocks:
                print("found at", col)
                return col
            
            col -= 1
        
        return None
    
    def _find_right(self, row, col, blocks):
        col += 1
        print("Looking for", [chr(block) for block in blocks], "to the right of", col)
        while col < self.columns:
            if self._blocks[row, col] in blocks:
                print("found at", col)
                return col

            col += 1
        
        return None
    
    def add_water(self, report=None):
        settled = True
        while settled:
            row, col = 0 - self.top, 500 - self.left
            settled = False
            while row < self.rows - 1:
                print(row, col)
                if self._blocks[row, col] == SAND:
                    print("wetting sand")
                    self._blocks[row, col] = DRIED_SAND
                elif self._blocks[row+1, col] in (SAND, DRIED_SAND):
                    print("drop down")
                    row += 1
                else:
                    lcol = self._find_left(row, col, (SAND, CLAY, WATER))
                    if lcol:
                        if self._blocks[row, lcol] == SAND:
                            print("sand to left")
                            col = lcol
                            continue
                        
                        rcol = self._find_right(row, col, (SAND, CLAY, WATER))
                        if rcol:
                            if self._blocks[row, rcol] == SAND:
                                print("sand to right")
                                col = rcol
                                continue
                            
                            print("valid square")
                            self._blocks[row, col] = WATER
                            settled = True
                            break
                        else:
                            print("flowing to right")
                            col = self._find_right(row, col, (DRIED_SAND,))
                    else:
                        rcol = self._find_right(row, col, (SAND, CLAY, WATER))
                        if self._blocks[row, rcol] == SAND:
                            print("sand to right")
                            col = rcol
                            continue
                        
                        print("flowing to left")
                        col = self._find_left(row, col, (DRIED_SAND))

            
            num_water = np.sum(self._blocks == WATER)
            if report and num_water % report == 0:
                print(self)

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
    
    ground.add_water(5 if args.verbose else None)

if __name__ == "__main__":
    day17()
