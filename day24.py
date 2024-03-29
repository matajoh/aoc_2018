""" Solution to day 24 of the 2018 Advent of Code """

import logging
from collections import namedtuple, deque

from utils import read_input, parse_args, Tokenizer, diff


class Unit(namedtuple("Unit", ("hit_points", "attack_power", "attack_type",
                               "initiative", "weaknesses", "immunities"))):
    """ Class representing a unit type """

    def __lt__(self, other):
        return self.initiative > other.initiative

    def _weak_immune_text(self):
        if self.immunities or self.weaknesses:
            parts = ["("]
            if self.immunities:
                parts.append("immune to {}".format(
                    ", ".join(sorted(self.immunities))))

            if self.weaknesses:
                if self.immunities:
                    parts.append("; ")

                parts.append("weak to {}".format(
                    ", ".join(sorted(self.weaknesses))))

            parts.append(") ")

            return "".join(parts)

        return ""

    def weak_to(self, unit):
        """ Whether this unit is weak to another unit's attack """
        return unit.attack_type in self.weaknesses

    def immune_to(self, unit):
        """ Whether this unit is immune to another unit's attack """
        return unit.attack_type in self.immunities

    def boost(self, value):
        """ Boosts this unit's attack power """
        return Unit(self.hit_points,
                    self.attack_power + value,
                    self.attack_type,
                    self.initiative,
                    self.weaknesses,
                    self.immunities)

    def __repr__(self):
        template = "{} hit points {}with an attack that does {} {} damage at initiative {}"
        return template.format(
            self.hit_points,
            self._weak_immune_text(),
            self.attack_power,
            self.attack_type,
            self.initiative
        )


class Group:
    """ Class representing a group of units """

    def __init__(self, unit, num_units, membership, index):
        self.unit = unit
        self.num_units = num_units
        self.membership = membership
        self.index = index

    def boost(self, value):
        """ Boosts this group """
        self.unit = self.unit.boost(value)

    @property
    def effective_power(self):
        """ Returns this group's effective power """
        return self.num_units * self.unit.attack_power

    ATTACK_TEMPLATE = "%s group %d attacks defending group %d, killing %d units"

    def attack(self, target):
        """ Attack the target """
        damage = self.effective_power
        if target.unit.weak_to(self.unit):
            damage *= 2

        num_units = target.take_damage(damage)
        logging.debug(Group.ATTACK_TEMPLATE,
                      self.membership,
                      self.index,
                      target.index,
                      num_units
                      )

    def take_damage(self, damage):
        """ Take damage from an attack """
        num_killed = damage // self.unit.hit_points
        num_killed = min(num_killed, self.num_units)
        self.num_units -= num_killed
        return num_killed

    def __lt__(self, other):
        if self.effective_power > other.effective_power:
            return True

        if self.effective_power == other.effective_power:
            assert self.unit.initiative != other.unit.initiative
            return self.unit.initiative > other.unit.initiative

        return False

    SELECT_TEMPLATE = "{} group {} would deal defending group {} {} damage"

    def select_target(self, groups):
        """ Select a target to attack """

        max_damage = 0
        target = None
        for group in groups:
            damage = self.effective_power
            if group.unit.weak_to(self.unit):
                damage *= 2
            elif group.unit.immune_to(self.unit):
                damage = 0

            if damage == 0:
                continue

            logging.debug(Group.SELECT_TEMPLATE, self.membership,
                          self.index, group.index, damage)

            if damage > max_damage:
                max_damage = damage
                target = group
            elif damage == max_damage:
                if group.effective_power > target.effective_power:
                    target = group
                elif group.effective_power == target.effective_power:
                    if group.unit.initiative > target.unit.initiative:
                        target = group
                    else:
                        assert target.unit.initiative != group.unit.initiative

        return target

    @staticmethod
    def parse(text, membership, index):
        """ Parse a group from the line of text """

        tokens = Tokenizer(text)
        num_units = tokens.read_int()
        tokens.consume(" units each with ")

        hit_points = tokens.read_int()
        tokens.consume(" hit points ")

        weaknesses = []
        immunities = []
        if tokens.peek() == '(':
            tokens.consume('(')
            while tokens.peek() != ')':
                if tokens.peek() == 'w':
                    tokens.consume("weak to ")
                    list_text = tokens.read_until(')', ';')
                    weaknesses = [part.strip()
                                  for part in list_text.split(',')]
                elif tokens.peek() == 'i':
                    tokens.consume("immune to ")
                    list_text = tokens.read_until(')', ';')
                    immunities = [part.strip()
                                  for part in list_text.split(',')]
                elif tokens.peek() == ';':
                    tokens.consume(';')
                    tokens.skip_whitespace()

            tokens.consume(') ')

        tokens.consume("with an attack that does ")
        attack_power = tokens.read_int()
        attack_type = tokens.read_word()
        tokens.consume(" damage at initiative ")
        initiative = tokens.read_int()

        unit = Unit(hit_points, attack_power, attack_type,
                    initiative, set(weaknesses), set(immunities))
        group = Group(unit, num_units, membership, index)
        if str(group) != text:
            logging.debug(diff(str(group), text))

        return group

    def __repr__(self):
        return "{} units each with {}".format(self.num_units, self.unit)


def parse_groups(lines):
    """ Parse the Immune System and Infection groups from the input """
    if not isinstance(lines, deque):
        lines = deque(lines)

    assert lines.popleft().strip() == "Immune System:"
    immune = []
    while lines:
        line = lines.popleft().strip()
        if line:
            immune.append(Group.parse(
                line, "Immune System", len(immune) + 1))
        else:
            break

    assert lines.popleft().strip() == "Infection:"
    infection = []
    while lines:
        line = lines.popleft().strip()
        if line:
            infection.append(Group.parse(line, "Infection",
                                         len(infection) + 1))
        else:
            break

    return immune, infection


def add_army_state(army, lines):
    """ Add state about an army to the list of lines """
    if army:
        for group in army:
            lines.append("Group {} contains {} units".format(
                group.index, group.num_units))
    else:
        lines.append("No groups remain.")


def battle_state(immune, infection):
    """ Return a string representing the state of the battle """
    lines = ["Immune System:"]
    add_army_state(immune, lines)
    lines.append("Infection:")
    add_army_state(infection, lines)
    return "\n".join(lines)


def count_units(army):
    """ Count the number of units in an army """
    num_units = 0
    for group in army:
        num_units += group.num_units

    return num_units


def selection_phase(immune, infection):
    """ Have the groups select targets """

    logging.debug("== SELEcTioN PHASE ==")

    groups = immune + infection
    groups = deque(sorted(groups))

    targets = {
        "Immune System": infection.copy(),
        "Infection": immune.copy()
    }

    selections = {}

    while groups:
        group = groups.popleft()
        target = group.select_target(targets[group.membership])
        if target:
            selections[group] = target
            targets[group.membership].remove(target)

    return selections


def attack_phase(immune, infection, selections):
    """ Have the groups attack their targets """
    logging.debug("== ATTACK PHASE ==")

    groups = immune + infection
    groups.sort(key=lambda group: group.unit.initiative, reverse=True)
    groups = deque(groups)

    while groups:
        group = groups.popleft()
        if group in selections:
            group.attack(selections[group])

    immune = list(filter(lambda group: group.num_units, immune))
    infection = list(filter(lambda group: group.num_units, infection))
    return immune, infection


def do_battle(immune, infection, boost=0):
    """ Perform a battle until it ends with one side winning or a draw """
    logging.debug("=== BATTLE START ===")

    if boost:
        for group in immune:
            group.boost(boost)

    while immune and infection:
        if logging.DEBUG >= logging.root.level:
            logging.debug(battle_state(immune, infection))

        before = count_units(immune) + count_units(infection)
        selections = selection_phase(immune, infection)
        immune, infection = attack_phase(immune, infection, selections)

        after = count_units(immune) + count_units(infection)

        if before == after:
            logging.debug("STALEMATE")

            break

    return immune, infection


def test_day24():
    """ Test for the day 24 solution """
    lines = read_input(24, True)
    line_queue = deque(lines)
    immune, infection = parse_groups(line_queue)

    expected = []
    while line_queue:
        expected.append(line_queue.popleft().strip())

    expected = "\n".join(expected)

    immune, infection = do_battle(immune, infection)

    actual = battle_state(immune, infection)
    assert actual == expected, diff(actual, expected)

    expected = 5216
    actual = count_units(infection)
    assert actual == expected, "{} != {}".format(actual, expected)

    immune, infection = parse_groups(lines)
    immune, infection = do_battle(immune, infection, 1570)

    expected = 51
    actual = count_units(immune)
    assert actual == expected, "{} != {}".format(actual, expected)


def part1(lines):
    """ Solution to part 1 """
    immune, infection = parse_groups(lines)

    immune, infection = do_battle(immune, infection)
    if immune:
        return count_units(immune)

    if infection:
        return count_units(infection)

    raise ValueError("No winner")


def find_boost(lines, start, end):
    """ Perform a binary search to find the right amount of boost """
    logging.debug("Evaluating range %d => %d", start, end)
    if start + 1 == end:
        return end

    boost = (start + end) // 2
    immune, infection = parse_groups(lines)
    immune, infection = do_battle(immune, infection, boost)

    if immune and infection:
        return find_boost(lines, boost, end)

    if immune:
        return find_boost(lines, start, boost)

    return find_boost(lines, boost, end)


def part2(lines):
    """ Solution to part 2 """
    boost = find_boost(lines, 0, 100)

    immune, infection = parse_groups(lines)
    immune, infection = do_battle(immune, infection, boost)

    assert immune
    assert not infection
    return count_units(immune)


def day24():
    """ Solution to day 24 """
    parse_args()

    lines = read_input(24)

    print("Part 1")
    print(part1(lines))

    print("Part 2")
    print(part2(lines))


if __name__ == "__main__":
    day24()
