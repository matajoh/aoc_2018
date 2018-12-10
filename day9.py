""" Solution to day 9 of the 2018 Advent of Code """

from collections import deque

from utils import parse_args

DEBUG = [
    (9, 25, 32),
    (10, 1618, 8317),
    (13, 7999, 146373),
    (17, 1104, 2764),
    (21, 6111, 54718),
    (30, 5807, 37305)
]
TEST = [(419, 72164, -1),
        (419, 7216400, -1)]
FORMAT = "{} players; last marble is worth {} points: high score is {} [{}]"


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


def print_circle(player, current):
    """ Prints the current state of the circle.

    Args:
        player -- the player who just went
        current -- the current marble
    """
    values = deque()
    marble = current
    values.append(marble.value)
    min_value = marble.value
    marble = marble.clockwise
    while marble != current:
        values.append(marble.value)
        if marble.value < min_value:
            min_value = marble.value

        marble = marble.clockwise

    while values[0] != min_value:
        values.append(values.popleft())

    if player is None:
        output = ["[-]"]
    else:
        output = ["[{}]".format(player)]

    for value in values:
        if value == current.value:
            output.append("({})".format(value))
        else:
            output.append(str(value))

    print(" ".join(output))


def play_game(num_players, last_marble, verbose):
    """ Plays a game

    Args:
        num_players -- the number of players
        last_marble -- the value of the last marble
        verbose -- whether to output the per-turn state
    """
    scores = [0]*num_players
    current = Marble(0)
    current.clockwise = current
    current.counterclockwise = current

    if verbose:
        print_circle(None, current)

    for i in range(last_marble):
        value = i + 1
        if value % 23 == 0:
            current, removed = current.remove()
            scores[i % num_players] += removed + value
        else:
            current = current.insert(value)

        if verbose:
            print_circle((i % num_players) + 1, current)

    num_expected = last_marble - 2 * (last_marble // 23) + 1
    num_actual = 1
    marble = current
    while marble.clockwise != current:
        marble = marble.clockwise
        num_actual += 1

    assert num_actual == num_expected, "{} != {}".format(
        num_actual, num_expected)
    return max(scores)


def day9():
    """ Solution to Day 9 """
    args = parse_args()

    if args.debug:
        games = DEBUG
    else:
        games = TEST

    for game in games:
        num_players, last_marble, expected_score = game
        actual_score = play_game(num_players, last_marble, args.verbose)
        print(FORMAT.format(num_players, last_marble,
                            actual_score, expected_score))
        if args.verbose:
            break


if __name__ == "__main__":
    day9()
