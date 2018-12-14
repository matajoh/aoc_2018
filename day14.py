""" Solution to day 14 of 2018 Advent of Code """

from copy import copy

from utils import parse_args

SCORES = [3, 7]

DEBUG_PART1 = [
    (9, "5158916779"),
    (5, "0124515891"),
    (18, "9251071085"),
    (2018, "5941429882")
]

DEBUG_PART2 = [
    ("51589", 9),
    ("01245", 5),
    ("92510", 18),
    ("59414", 2018)
]

TEST_PART1 = [
    (409551, None)
]

TEST_PART2 = [
    ("409551", None)
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

    print("".join(parts))


def grow_to_length(scores, length, verbose):
    """ Grow the scoreboard to the desired length """
    elf0 = 0
    elf1 = 1
    while len(scores) < length:
        if verbose:
            print_scoreboard(scores, elf0, elf1)

        recipe = scores[elf0] + scores[elf1]

        if recipe // 10:
            scores.append(1)

        scores.append(recipe % 10)

        elf0 = (elf0 + 1 + scores[elf0]) % len(scores)
        elf1 = (elf1 + 1 + scores[elf1]) % len(scores)

    return elf0, elf1


def part1(scores, start, verbose):
    """ Solution to part 1 """
    grow_to_length(scores, start+10, verbose)
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

    elf0, elf1 = grow_to_length(scores, len(sequence), False)

    while True:
        if len(scores) % 100000 == 0:
            print(len(scores))

        recipe = scores[elf0] + scores[elf1]

        if recipe // 10:
            scores.append(1)
            if check_for_match(scores, sequence):
                break

        scores.append(recipe % 10)
        if check_for_match(scores, sequence):
            break

        elf0 = (elf0 + 1 + scores[elf0]) % len(scores)
        elf1 = (elf1 + 1 + scores[elf1]) % len(scores)

    return len(scores) - len(sequence)


def day14():
    """ Solution to day 14 """
    args = parse_args()
    cases = DEBUG_PART1 if args.debug else TEST_PART1

    print("Part 1")
    for start, expected in cases:
        scores = copy(SCORES)
        actual = part1(scores, start, args.verbose)
        print(start, ":", actual, "(", expected, ")")

    cases = DEBUG_PART2 if args.debug else TEST_PART2
    print("Part 2")
    for sequence, expected in cases:
        scores = copy(SCORES)
        actual = part2(scores, sequence)
        print(sequence, ":", actual, "(", expected, ")")


if __name__ == "__main__":
    day14()
