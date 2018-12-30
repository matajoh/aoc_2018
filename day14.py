""" Solution to day 14 of 2018 Advent of Code """

from copy import copy
import logging

import pytest

from utils import parse_args

SCORES = [3, 7]

PART1_TESTS = [
    (9, "5158916779"),
    (5, "0124515891"),
    (18, "9251071085"),
    (2018, "5941429882")
]

PART2_TESTS = [
    ("51589", 9),
    ("01245", 5),
    ("92510", 18),
    ("59414", 2018)
]


def print_scoreboard(scores, elf0, elf1):
    """ Print out the current state of the scoreboard """
    parts = []
    for i, score in enumerate(scores):
        if i == elf0:
            text = "({})".format(score)
        elif i == elf1:
            text = "[{}]".format(score)
        else:
            text = " {} ".format(score)

        parts.append(text)

    logging.debug("".join(parts))


def grow_to_length(scores, length):
    """ Grow the scoreboard to the desired length """
    elf0 = 0
    elf1 = 1
    while len(scores) < length:
        if logging.DEBUG >= logging.root.level:
            print_scoreboard(scores, elf0, elf1)

        recipe = scores[elf0] + scores[elf1]

        if recipe // 10:
            scores.append(1)

        scores.append(recipe % 10)

        elf0 = (elf0 + 1 + scores[elf0]) % len(scores)
        elf1 = (elf1 + 1 + scores[elf1]) % len(scores)

    return elf0, elf1


def part1(scores, start):
    """ Solution to part 1 """
    grow_to_length(scores, start+10)
    parts = [str(score) for score in scores[start:start + 10]]
    return "".join(parts)


def check_for_match(scores, sequence):
    """ Check if the end of the list of scores matches the sequence """
    start = len(scores) - len(sequence)
    for i, score in enumerate(sequence):
        if score != scores[i + start]:
            return False

    return True


def part2(scores, sequence_text):
    """ Solution to part 2 """
    sequence = [int(char) for char in sequence_text]

    elf0, elf1 = grow_to_length(scores, len(sequence))
    assert sequence[-1] == 1
    check_prev = sequence[-2]

    prev = None
    while True:
        if len(scores) % 100000 == 0:
            logging.debug(len(scores))

        recipe = scores[elf0] + scores[elf1]

        if recipe // 10:
            scores.append(1)
            if prev == check_prev:
                if check_for_match(scores, sequence):
                    break

            prev = 1

        curr = recipe % 10
        scores.append(curr)
        if curr == 1 and prev == check_prev:
            if check_for_match(scores, sequence):
                break

        prev = curr
        elf0 = (elf0 + 1 + scores[elf0]) % len(scores)
        elf1 = (elf1 + 1 + scores[elf1]) % len(scores)

    return len(scores) - len(sequence)

@pytest.mark.parametrize("start, expected", PART1_TESTS)
def test_part1(start, expected):
    """ Test for part 1 """
    scores = copy(SCORES)
    actual = part1(scores, start)
    assert actual == expected

@pytest.mark.parametrize("sequence, expected", PART2_TESTS)
def test_part2(sequence, expected):
    """ Test for part 2 """
    scores = copy(SCORES)
    actual = part2(scores, sequence)
    assert actual == expected


def day14():
    """ Solution to day 14 """
    parse_args()

    print("Part 1")
    print(part1(copy(SCORES), 409551))

    print("Part 2")
    print(part2(copy(SCORES), "409551"))


if __name__ == "__main__":
    day14()
