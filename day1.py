""" Solution to day 1 of 2018 Advent of Code """

from utils import read_input


def line_to_int(line):
    """ Convert a line to an integer """
    line = line.strip()

    if line.startswith('+'):
        return int(line[1:])

    return -int(line[1:])


def part1(values):
    """ Solution to part 1 """
    print(sum(values, 0))


def part2(values):
    """ Solution to part 2 """
    frequencies = set([0])

    index = 0
    frequency = 0
    while True:
        found = False
        for value in values:
            frequency += value
            index += 1
            if frequency in frequencies:
                found = True
                break

            frequencies.add(frequency)

        if found:
            break

    print(frequency)


def day1():
    """ Day 1 solution """
    lines = read_input(1).split('\n')
    values = [line_to_int(line) for line in lines]

    print("Part 1")
    part1(values)
    print("Part 2")
    part2(values)


if __name__ == "__main__":
    day1()
