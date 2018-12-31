""" Solution to day 9 of the 2018 Advent of Code """

from collections import deque
import logging

import pytest

from utils import parse_args

TEST = [
    (9, 25, 32),
    (10, 1618, 8317),
    (13, 7999, 146373),
    (17, 1104, 2764),
    (21, 6111, 54718),
    (30, 5807, 37305)
]

FORMAT = "{} players; last marble is worth {} points: high score is {}"


class Marble:
    """ Class representing a marble (i.e. doubly-linked list) """

    def __init__(self, value):
        self.value = value
        self.clockwise = None
        self.counterclockwise = None

    def insert(self, value):
        """ Inserts a marble according to the rules """
        current = self.clockwise
        marble = Marble(value)
        marble.clockwise = current.clockwise
        marble.counterclockwise = current

        marble.clockwise.counterclockwise = marble
        marble.counterclockwise.clockwise = marble

        return marble

    def remove(self):
        """ Removes a marble according to the rules """
        current = self
        for _ in range(7):
            current = current.counterclockwise

        current.counterclockwise.clockwise = current.clockwise

        return current.clockwise, current.value

    def __repr__(self):
        return "Marble(value={})".format(self.value)


class Game:
    """ Class representing the marble game """

    def __init__(self, num_players):
        self.num_players = num_players
        self.scores = None
        self.current = None
        self.player = None
        self.reset()

    def reset(self):
        """ Resets the state of the game """
        self.scores = [0]*self.num_players
        self.current = Marble(0)
        self.current.clockwise = self.current
        self.current.counterclockwise = self.current
        self.player = None

    def __repr__(self):
        values = deque()
        marble = self.current
        values.append(marble.value)
        min_value = marble.value
        marble = marble.clockwise
        while marble != self.current:
            values.append(marble.value)
            if marble.value < min_value:
                min_value = marble.value

            marble = marble.clockwise

        while values[0] != min_value:
            values.append(values.popleft())

        if self.player is None:
            output = ["[-]"]
        else:
            output = ["[{}]".format(self.player + 1)]

        for value in values:
            if value == self.current.value:
                output.append("({})".format(value))
            else:
                output.append(str(value))

        return " ".join(output)

    def play(self, last_marble):
        """ Plays a game

        Args:
            last_marble -- the value of the last marble
        """
        logging.debug("%s", self)

        self.player = 0
        for i in range(last_marble):
            value = i + 1
            if value % 23 == 0:
                self.current, removed = self.current.remove()
                self.scores[self.player] += removed + value
            else:
                self.current = self.current.insert(value)

            logging.debug("%s", self)

            self.player = (self.player + 1) % self.num_players

        num_expected = last_marble - 2 * (last_marble // 23) + 1
        num_actual = 1
        marble = self.current
        while marble.clockwise != self.current:
            marble = marble.clockwise
            num_actual += 1

        assert num_actual == num_expected, "{} != {}".format(
            num_actual, num_expected)
        return max(self.scores)


@pytest.mark.parametrize("num_players, last_marble, expected", TEST)
def test_day9(num_players, last_marble, expected):
    """ Test for day 9 """
    game = Game(num_players)
    actual = game.play(last_marble)
    assert actual == expected


def day9():
    """ Solution to Day 9 """
    parse_args()

    game = Game(419)

    print("Part 1")
    print(game.play(72164))

    game.reset()

    print("Part 2")
    print(game.play(7216400))


if __name__ == "__main__":
    day9()
