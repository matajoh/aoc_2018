""" Solution to day 6 of the 2018 Advent of Code """

import numpy as np

from utils import read_input, parse_args


def read_location(line):
    """ Read a location from the provided line """
    parts = line.split(',')
    row = int(parts[1].strip())
    col = int(parts[0].strip())
    return row, col


def build_field(size, locations):
    """ Find the distances in the field to all locations """
    num_locations = len(locations)

    print("Building field...")
    field = np.zeros((num_locations, size, size), np.int32)
    values = np.arange(size*size).reshape(size, size)
    row_values = values // size
    col_values = values % size
    for i, (row, col) in enumerate(locations):
        field[i] = np.abs(row_values - row) + np.abs(col_values - col)

    return field


def largest_finite_area(field):
    """ Find the largest finite area """

    num_locations = field.shape[0]
    min_dist = np.min(field, axis=0)
    num_nearby = np.sum(field == min_dist, axis=0)
    nearest = np.where(num_nearby == 2, -1, np.argmin(field, axis=0))

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

    return max_size


def find_nearest_region(field, dist_sum):
    """ Find largest region nearest to all coordinates """
    summed = np.sum(field, axis=0)
    region = summed < dist_sum
    return np.sum(region)


def test_day6():
    """ Test for day 6 """
    size = 10
    dist_sum = 32
    lines = ["1, 1",
             "1, 6",
             "8, 3",
             "3, 4",
             "5, 5",
             "8, 9"]

    locations = [read_location(line) for line in lines]
    field = build_field(size, locations)

    expected = 17
    actual = largest_finite_area(field)
    assert actual == expected

    expected = 16
    actual = find_nearest_region(field, dist_sum)
    assert actual == expected


def day6():
    """ Solution to day 6 """
    parse_args()

    size = 400
    dist_sum = 10000
    lines = read_input(6)

    locations = [read_location(line) for line in lines]
    field = build_field(size, locations)

    print("Part 1")
    print(largest_finite_area(field))

    print("Part 2")
    print(find_nearest_region(field, dist_sum))


if __name__ == "__main__":
    day6()
