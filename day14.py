from utils import parse_args
from copy import copy

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

def try_recipes(scores, elf0, elf1):
    if elf0 == elf1:
        recipe = scores[elf0]
    else:
        recipe = scores[elf0] + scores[elf1]

    if recipe // 10:
        scores.append(1)
    
    scores.append(recipe % 10)

    elf0 = (elf0 + 1 + scores[elf0]) % len(scores)
    elf1 = (elf1 + 1 + scores[elf1]) % len(scores)

    return elf0, elf1


def grow_to_length(scores, length, verbose):
    elf0 = 0
    elf1 = 1
    while len(scores) < length:
        if verbose:
            print_scoreboard(scores, elf0, elf1)

        elf0, elf1 = try_recipes(scores, elf0, elf1)

    return elf0, elf1

def part1(scores, start, verbose):
    grow_to_length(scores, start+10, verbose)
    parts = [str(score) for score in scores[start:start + 10]]
    return "".join(parts)

def part2(scores, sequence):
    sequence = [int(char) for char in sequence]
    
    elf0, elf1 = grow_to_length(scores, len(sequence), False)

    best_match = 0
    while True:
        if len(scores) % 10000 == 0:
            print(len(scores), best_match)

        start = len(scores) - len(sequence)
        found = True
        for i, score in enumerate(sequence):
            best_match = max([best_match, i])
            if score != scores[i + start]:
                found = False
                break
        
        if found:
            break
        
        elf0, elf1 = try_recipes(scores, elf0, elf1)
    
    return len(scores) - len(sequence)


def day14():
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
