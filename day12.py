""" Solution to day 12 of the 2018 Advent of Code """

import numpy as np

from utils import parse_args, read_input


def move(pot, count):
    """ Move the pot by count """
    if pot is None:
        return None

    if count < 0:
        return move(pot.prev, count + 1)

    if count > 0:
        return move(pot.next, count - 1)

    return pot


class Rule:
    """ Class representing a growth rule """

    def __init__(self, line):
        parts = line.split('=>')
        pattern = [ord(plant) for plant in parts[0].strip()]
        self.has_plant = np.array(pattern) == ord('#')
        self.will_grow = parts[1].strip() == '#'

    def apply(self, neighbor_state):
        """ Apply this rule to the provided neighbor state """
        if (neighbor_state == self.has_plant).all():
            return self.will_grow

        return None

    def __repr__(self):
        pattern = "".join(np.where(self.has_plant, '#', '.'))
        will_grow = '#' if self.will_grow else '.'
        return "{} => {}".format(pattern, will_grow)


NEIGHBORS = [-2, -1, 0, 1, 2]


class Pot:
    """ Class representing a pot with a plant """

    def __init__(self, index, has_plant, next_pot=None, prev_pot=None):
        self.index = index
        self.has_plant = has_plant
        self.will_have_plant = False
        self.neighbor_state = np.zeros(5, np.bool)
        self.next = next_pot
        self.prev = prev_pot

    def _fill_neighbors(self):
        neighbors = [move(self, distance) for distance in NEIGHBORS]
        for i, neighbor in enumerate(neighbors):
            if neighbor:
                self.neighbor_state[i] = neighbor.has_plant
            else:
                self.neighbor_state[i] = False

    def apply_rule(self, rule):
        """ Apply this rule to the pot """
        self._fill_neighbors()
        will_grow = rule.apply(self.neighbor_state)
        if will_grow is not None:
            self.will_have_plant = will_grow

    def update(self):
        """ Update this pot to the next state """
        if self.will_have_plant is not None:
            self.has_plant = self.will_have_plant

        self.will_have_plant = False

    def __repr__(self):
        return "{}:{}".format(self.index, '#' if self.has_plant else '.')


def build_state_string(pot, states):
    """ Build a state string """

    if pot is None:
        return "".join(states)
    else:
        states.append('#' if pot.has_plant else '.')
        return build_state_string(pot.next, states)


def count_pots(pot):
    """ Count the pots with plants """

    if pot is None:
        return 0

    if pot.has_plant:
        count = pot.index
    else:
        count = 0

    return count + count_pots(pot.next)


def parse_input(lines):
    """ Parse the problem input """

    initial_state = lines[0][15:]
    first = Pot(-1, False)
    current = first
    for i, has_plant in enumerate(initial_state):
        current.next = Pot(i, has_plant == '#')
        current.next.prev = current
        current = current.next

    assert build_state_string(first.next, []) == initial_state

    rules = []
    for line in lines[2:]:
        rule = Rule(line)
        assert str(rule) == line.strip(), "{} != {}".format(rule, line)
        rules.append(rule)

    return first, rules


def grow_plants(generations, first_pot, rules, verbose):
    """ Grow the plants for the specified generations """
    last_pot = first_pot
    while last_pot.next is not None:
        last_pot = last_pot.next

    counts = []
    for generation in range(generations):
        while first_pot.has_plant or first_pot.next.has_plant or first_pot.next.next.has_plant:
            first_pot = Pot(first_pot.index - 1, False, next_pot=first_pot)
            first_pot.next.prev = first_pot

        while last_pot.has_plant or last_pot.prev.has_plant or last_pot.prev.prev.has_plant:
            last_pot = Pot(last_pot.index + 1, False, prev_pot=last_pot)
            last_pot.prev.next = last_pot

        if verbose:
            print("{0:02d}: {1}".format(generation,
                                        build_state_string(first_pot, [])))
        else:
            counts.append(count_pots(first_pot))

        current = first_pot
        while current is not None:
            for rule in rules:
                current.apply_rule(rule)

            current = current.next

        current = first_pot
        while current is not None:
            current.update()
            current = current.next

    if verbose:
        print("{}:".format(generations), build_state_string(first_pot, []))
    else:
        counts.append(count_pots(first_pot))

    return counts


def day12():
    """ Solution to day 12 """
    args = parse_args()
    lines = read_input(12, args.debug).split('\n')

    first_pot, rules = parse_input(lines)
    print("Part 1")
    counts = grow_plants(20, first_pot, rules, args.verbose)
    print("Final count:", counts[-1])

    first_pot, rules = parse_input(lines)
    print("Part 2")
    x = 200
    counts = grow_plants(x, first_pot, rules, args.verbose)

    y = counts[-1]
    slope = counts[-1] - counts[-2]

    increase = 50000000000 - x
    count = increase*slope + y
    print("Final count:", count)


if __name__ == "__main__":
    day12()
