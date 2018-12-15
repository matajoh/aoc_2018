from collections import deque
import heapq
from copy import copy

import numpy as np

from utils import read_input, parse_args

DEBUG_OUTCOMES = [
    27730,
    36334,
    39514,
    27755,
    28944,
    18740
]

CLEAR = ord('.')
WALL = ord('#')
ELF = ord('E')
GOBLIN = ord('G')

DEFAULT_HEALTH = 200
DEFAULT_ATTACK = 3

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)

    return total_path

def heuristic(first, second):
    return np.abs(first[0]-second[0]) + np.abs(first[1]-second[1])

def neighbors(point):
    row, col = point
    for drow, dcol in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
        yield row + drow, col + dcol

class Unit:
    def __init__(self, race, battle, index, health=DEFAULT_HEALTH, attack=DEFAULT_ATTACK):
        self.race = race
        self.battle = battle
        self.enemy = GOBLIN if race == ELF else ELF
        self.health_points = health
        self.attack_power = attack
        self.index = index
    
    def take_damage(self, damage):
        self.health_points -= damage
        if self.health_points <= 0:
            self.battle.remove(self)
    
    def __lt__(self, other):
        return self.index < other.index
    
    def attack(self):
        min_hp = DEFAULT_HEALTH
        targets = []
        for neighbor in neighbors(self.index):
            other = self.battle[neighbor]
            if other is None or other.race == self.race:
                continue
            
            if other.health_points < min_hp:
                min_hp = other.health_points
                targets = [other]
            elif other.health_points == min_hp:
                targets.append(other)

        if targets:
            targets.sort()   
            targets[0].take_damage(self.attack_power)
    
    def find_nearest(self, goals):
        min_targets = []
        min_dist = self.battle.max_dist
        for goal in goals:
            path = self.battle.find_min_path(self.index, goal)
            if path is None:
                continue
                           
            if len(path) < min_dist:
                min_dist = len(path)
                min_targets = [goal]
            elif len(path) == min_dist:
                min_targets.append(goal)
        
        if not min_targets:
            return None, min_dist

        min_targets.sort()
        return min_targets[0], min_dist
        
    
    def move(self, goals):
        goal, dist = self.find_nearest(goals)

        if goal is None:
            return

        moves = []
        for neighbor in neighbors(self.index):
            paths = self.battle.find_all_paths(neighbor, goal, dist - 2, [])
            if paths:
                moves.append(neighbor)

        moves.sort()
        self.battle.move(self, moves[0])
    
    def take_turn(self):
        in_range = self.battle.find_in_range(self.enemy)
        if not in_range:
            return True

        if self.index in in_range:
            self.attack()
        else:
            valid_goals = list(filter(self.battle.is_clear, in_range))
            self.move(valid_goals)
            if self.index in in_range:
                self.attack()
        
        return False
    
    @property
    def alive(self):
        return self.health_points > 0
    
    def __repr__(self):
        return "{}({})".format(chr(self.race), self.health_points)  

class Battle:
    def __init__(self, lines):
        lines = [[ord(char) for char in line] for line in lines]
        lines = np.array(lines)

        self.num_rounds = 0
        self._max_dist = np.prod(lines.shape)
        self._walls = lines == WALL
        self._units = np.zeros(lines.shape, np.dtype(Unit))
        for ravel, spec in enumerate(lines.flatten()):
            index = np.unravel_index(ravel, lines.shape)
            if spec not in (ELF, GOBLIN):
                self._units[index] = None
            else:
                self._units[index] = Unit(spec, self, index)
    
    def to_string(self, omit_health=False):
        lines = []
        for wall_row, unit_row in zip(self._walls, self._units):
            blocks = [chr(WALL) if wall else chr(CLEAR) for wall in wall_row]
            
            units = []
            for col, unit in enumerate(unit_row):
                if unit:
                    blocks[col] = chr(unit.race)
                    units.append(str(unit))

            field_text = "".join(blocks)
            if omit_health:
                lines.append(field_text)
            else:
                unit_text = ", ".join(units)
                lines.append("{}   {}".format(field_text, unit_text).strip())

        return "\n".join(lines)

    @property
    def max_dist(self):
        return self._max_dist
    
    def find_in_range(self, race):
        in_range = set()
        for index, unit in enumerate(self._units.flatten()):
            if unit is None or unit.race != race:
                continue

            point = np.unravel_index(index, self._units.shape)

            for neighbor in neighbors(point):
                if not self._walls[neighbor]:
                    in_range.add(neighbor)
        
        return in_range
    
    def find_min_path(self, start, goal):
        closed_set = []
        open_set = [start]
        came_from = {}
        g_scores = {}
        g_scores[start] = 0
        f_scores = {}
        f_scores[start] = heuristic(start, goal)
        while open_set:
            current = open_set[0]
            f_score = f_scores[current]
            for point in open_set[1:]:
                if f_scores[point] < f_score:
                    f_score = f_scores[point]
                    current = point
            
            if current == goal:
                return reconstruct_path(came_from, current)
            
            open_set.remove(current)
            closed_set.append(current)

            if self._walls[current]:
                continue
            
            if self._units[current] and current != start:
                continue

            for neighbor in neighbors(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_scores[current] + 1
                if neighbor not in open_set:
                    open_set.append(neighbor)
                elif tentative_g_score >= g_scores[neighbor]:
                    continue
                
                came_from[neighbor] = current
                g_scores[neighbor] = tentative_g_score
                f_scores[neighbor] = g_scores[neighbor] + heuristic(neighbor, goal)
            
        return None         

    def find_all_paths(self, node, goal, length, path):
        if node in path:
            return []

        path.append(node)
        if length == 0:
            if node == goal:
                return [path]
            
            return []
        else:
            if self._walls[node] or self._units[node] is not None:
                return []
            
            paths = []
            for neighbor in neighbors(node):
                paths += self.find_all_paths(neighbor, goal, length-1, copy(path))
           
            return paths
    
    def __repr__(self):
        return self.to_string()
    
    def is_clear(self, index):
        if self._walls[index] or self._units[index] is not None:
            return False
        
        return True
    
    def move(self, unit, index):
        assert self._units[unit.index] == unit
        assert self._units[index] is None
        self._units[unit.index] = None
        self._units[index] = unit
        unit.index = index
    
    def remove(self, unit):
        self._units[unit.index] = None
    
    def __getitem__(self, key):
        return self._units[key]
    
    def round(self):
        over = False
        for unit in self._units.flatten():
            if unit is None or not unit.alive: 
                continue

            over = unit.take_turn()
            if over:
                break

        if over:
            return True

        self.num_rounds += 1
        return False
        
    @property
    def winners(self):
        race = None
        sum = 0
        for unit in self._units.flatten():
            if unit is None or not unit.alive:
                continue
            
            if unit.race == ELF:
                race = "Elves"
            else:
                race = "Goblins"
            
            sum += unit.health_points
        
        return race, sum


def read_start_state(lines):
    start_lines = []
    while lines:
        line = lines.popleft().strip()
        if len(line) == 0:
            break
        
        start_lines.append(line)
    
    return Battle(start_lines), "\n".join(start_lines)

def read_end_state(lines):
    end_lines = []
    while lines:
        line = lines.popleft().strip()
        if len(line) == 0:
            break

        end_lines.append(line)
    
    return "\n".join(end_lines)

def part1(battle, expected, verbose):
    if verbose:
        print("Round", battle.num_rounds)
        print(battle)

    while not battle.round():
        if verbose:
            print("Round", battle.num_rounds)
            print(battle)

    if verbose:
        print("Final")
        print(battle)

    if expected:
        assert str(battle) == expected, "{}\n{}".format(battle, expected)


def day15():
    args = parse_args()

    if args.debug:
        lines = read_input(15, True)
        lines = deque(lines.split('\n'))
        outcomes = DEBUG_OUTCOMES
    else:
        lines = read_input(15)
        lines = deque(lines.split('\n'))
        outcomes = [None]
    
    case = 0
    print("Part 1")
    while lines:
        battle, expected = read_start_state(lines)
        assert battle.to_string(True) == expected

        if lines:
            expected = read_end_state(lines)
        else:
            expected = None
        
        part1(battle, expected, args.verbose)
        race, sum = battle.winners
        print("Combat ends after", battle.num_rounds, "full rounds")
        print(race, "win with", sum, "total hit points left")
        print("Outcome:", battle.num_rounds, "*", sum, "=", sum*battle.num_rounds)
        print("( Expected:", outcomes[case], ")")
        case += 1


if __name__ == "__main__":
    day15()
