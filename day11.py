""" Solution to day 11 of the 2018 Advent of Code """

import numpy as np

from utils import parse_args

DEBUG_CELLS = [
    (122, 79, 57, -5),
    (217, 196, 39, 0),
    (101, 153, 71, 4)
]

DEBUG_PART1_GRIDS = [
    (18, 33, 45, 29),
    (42, 21, 61, 30)
]

DEBUG_PART2_GRIDS = [
    (18, 90, 269, 16, 113),
    (42, 232, 251, 12, 119)
]


def compute_cell_power_level(x, y, serial_number):
    """ Compute the power level of a cell """
    rack_id = x + 10
    power_level = rack_id * y
    power_level += serial_number
    power_level *= rack_id
    power_level //= 100
    power_level %= 100
    power_level %= 10
    return power_level - 5


def find_max_region(grid, region_size, verbose):
    """ Find the region with the maximum power level. """

    grid_size = grid.shape[0]
    max_sum = region_size*region_size*-5
    max_region = None
    for x in range(grid_size - region_size + 1):
        for y in range(grid_size - region_size + 1):
            region = grid[y:y+region_size, x:x+region_size]
            if region.sum() > max_sum:
                max_sum = region.sum()
                max_region = (x, y)

    if verbose:
        print(region_size, max_region, max_sum)

    return max_region


def build_grid(serial_number, grid_size):
    """ Build a grid using the provided serial number and size """

    grid = np.zeros((grid_size, grid_size), np.int32)
    for x in range(grid_size):
        for y in range(grid_size):
            grid[y, x] = compute_cell_power_level(x, y, serial_number)

    return grid


def part1(serial_number, grid_size, verbose):
    """ Solution to part 1 """

    grid = build_grid(serial_number, grid_size)

    x, y = find_max_region(grid, 3, verbose)
    region = grid[y:y+3, x:x+3]

    if verbose:
        print(grid[y-1:y+4, x-1:x+4])

    return x, y, region.sum()


def part2(serial_number, grid_size, max_region_size, verbose):
    """ Solution to part 2 """
    grid = build_grid(serial_number, grid_size)

    max_region = None
    max_sum = max_region_size*max_region_size*-5
    for region_size in range(1, max_region_size):
        x, y = find_max_region(grid, region_size, verbose)
        region = grid[y:y+region_size, x:x+region_size]
        if region.sum() > max_sum:
            max_sum = region.sum()
            max_region = x, y, region_size

    x, y, region_size = max_region
    return x, y, region_size, max_sum


def day11():
    """ Solution to day 11 """
    args = parse_args()

    if args.debug:
        for x, y, serial_number, expected in DEBUG_CELLS:
            actual = compute_cell_power_level(x, y, serial_number)
            assert actual == expected

        for test_case in DEBUG_PART1_GRIDS:
            serial_number, exp_x, exp_y, exp_sum = test_case
            act_x, act_y, act_sum = part1(serial_number, 300, args.verbose)
            assert act_x == exp_x
            assert act_y == exp_y
            assert act_sum == exp_sum

        for test_case in DEBUG_PART2_GRIDS:
            serial_number, exp_x, exp_y, exp_size, exp_sum = test_case
            act_x, act_y, act_size, act_sum = part2(serial_number, 300,
                                                    30, args.verbose)
            assert act_x == exp_x
            assert act_y == exp_y
            assert act_size == exp_size
            assert act_sum == exp_sum
    else:
        x, y, _ = part1(3031, 300, args.verbose)
        print("Part 1")
        print("{},{}".format(x, y))

        x, y, region_size, _ = part2(3031, 300, 30, args.verbose)
        print("Part 2")
        print("{},{},{}".format(x, y, region_size))


if __name__ == "__main__":
    day11()
