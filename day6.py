""" Solution to day 6 of the 2018 Advent of Code """

import numpy as np

from utils import read_input


def read_location(line):
    """ Read a location from the provided line """
    parts = line.split(',')
    row = int(parts[1].strip())
    col = int(parts[0].strip())
    return row, col


def part1(field):
    """ Solution to part 1 """

    size, _, num_locations = field.shape
    nearest = np.zeros((size, size), np.int32)
    for row in range(size):
        for col in range(size):
            min_dist = np.min(field[row, col])
            if np.sum(field[row, col] == min_dist) == 2:
                nearest[row, col] = -1
            else:
                nearest[row, col] = np.argmin(field[row, col])

    edges = set()
    edges = edges.union(nearest[0])
    edges = edges.union(nearest[-1])
    edges = edges.union(nearest[:, 0])
    edges = edges.union(nearest[:, -1])

    max_size = 0
    for location in range(num_locations):
        if location in edges:
            continue

        size = np.sum(nearest == location)
        if size > max_size:
            max_size = size

    print(max_size)


def part2(field, dist_sum):
    """ Solution to part 2 """
    summed = np.sum(field, axis=2)
    region = summed < dist_sum
    print(np.sum(region))


def day6(debug):
    """ Solution to day 6 """

    if debug:
        size = 10
        dist_sum = 32
        lines = "1, 1\n1, 6\n8, 3\n3, 4\n5, 5\n8, 9".split('\n')
    else:
        size = 400
        dist_sum = 10000
        lines = read_input(6).split('\n')

    locations = [read_location(line) for line in lines]
    num_locations = len(locations)

    print("Building field...")
    field = np.zeros((size, size, num_locations), np.int32)
    for i, (row, col) in enumerate(locations):
        for rrow in range(size):
            for ccol in range(size):
                field[rrow, ccol, i] = np.abs(row-rrow) + np.abs(col-ccol)

    print("Part 1")
    part1(field)

    print("Part 2")
    part2(field, dist_sum)


if __name__ == "__main__":
    day6(False)
