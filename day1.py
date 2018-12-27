""" Solution to day 1 of 2018 Advent of Code """

from utils import read_input


def find_repeating_frequency(values):
    """ Find the first time a running sum repeats """
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

    return frequency


def day1():
    """ Day 1 solution """
    lines = read_input(1)
    values = [int(line) for line in lines]

    print("Part 1")
    print(sum(values, 0))
    print("Part 2")
    print(find_repeating_frequency(values))


if __name__ == "__main__":
    day1()
