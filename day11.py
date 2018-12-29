""" Solution to day 11 of the 2018 Advent of Code """

import logging

import numpy as np
import pytest

from utils import parse_args

TEST_PART1_GRIDS = [
    (18, 33, 45, 29),
    (42, 21, 61, 30)
]

TEST_PART2_GRIDS = [
    (18, 90, 269, 16, 113),
    (42, 232, 251, 12, 119)
]


class IntegralImage:
    """ Implements an integral image (or Summed Area Table) """

    def __init__(self, image):
        rows, cols = image.shape
        self._values = np.zeros((rows+1, cols+1), np.int64)
        for row in range(rows):
            row_sum = 0
            for col in range(cols):
                row_sum += image[row, col]
                above = self._values[row, col+1]
                self._values[row+1, col+1] = row_sum + above

    def find_max_region(self, size):
        """ Finds the maximum region of the specified size """
        rows, cols = self.shape
        region_sums = np.zeros((rows-size, cols-size), np.int64)
        region_sums += self._values[size:, size:]
        region_sums -= self._values[size:, :cols-size]
        region_sums -= self._values[:rows-size, size:]
        region_sums += self._values[:rows-size, :cols-size]
        max_region = np.argmax(region_sums)
        max_region = np.unravel_index(max_region, region_sums.shape)
        max_sum = region_sums[max_region]

        logging.debug("%d %s %d", size, max_region, max_sum)

        return max_region, max_sum

    @property
    def shape(self):
        """ The shape of the integral image """
        return self._values.shape


def build_grid(serial_number, grid_size):
    """ Build a grid using the provided serial number and size """

    values = np.arange(grid_size*grid_size,
                       dtype=np.int32).reshape(grid_size, grid_size)
    x_values = values % grid_size
    y_values = values // grid_size
    grid = np.zeros((grid_size, grid_size), np.int32)
    rack_id = x_values + 10
    grid = rack_id * y_values
    grid += serial_number
    grid *= rack_id
    grid //= 100
    grid %= 100
    grid %= 10
    grid -= 5
    return grid


def part1(serial_number, grid_size):
    """ Solution to part 1 """

    grid = build_grid(serial_number, grid_size)
    integral_image = IntegralImage(grid)

    (y, x), region_sum = integral_image.find_max_region(3)

    logging.debug("%s", grid[y-1:y+4, x-1:x+4])

    return x, y, region_sum


def part2(serial_number, grid_size, max_region_size):
    """ Solution to part 2 """
    grid = build_grid(serial_number, grid_size)
    integral_image = IntegralImage(grid)

    max_region = None
    max_sum = max_region_size*max_region_size*-5
    for region_size in range(1, max_region_size):
        (y, x), region_sum = integral_image.find_max_region(region_size)
        if region_sum > max_sum:
            max_sum = region_sum
            max_region = x, y, region_size

    x, y, region_size = max_region
    return x, y, region_size, max_sum


@pytest.mark.parametrize("serial_number, exp_x, exp_y, exp_sum", TEST_PART1_GRIDS)
def test_part1(serial_number, exp_x, exp_y, exp_sum):
    """ Tests for part 1 """
    act_x, act_y, act_sum = part1(serial_number, 300)
    assert act_x == exp_x
    assert act_y == exp_y
    assert act_sum == exp_sum


@pytest.mark.parametrize("serial_number, exp_x, exp_y, exp_size, exp_sum", TEST_PART2_GRIDS)
def test_part2(serial_number, exp_x, exp_y, exp_size, exp_sum):
    """ Tests for part 2 """
    act_x, act_y, act_size, act_sum = part2(serial_number, 300, 30)
    assert act_x == exp_x
    assert act_y == exp_y
    assert act_size == exp_size
    assert act_sum == exp_sum


def day11():
    """ Solution to day 11 """
    parse_args()

    x, y, _ = part1(3031, 300)
    print("Part 1")
    print("{},{}".format(x, y))

    x, y, region_size, _ = part2(3031, 300, 30)
    print("Part 2")
    print("{},{},{}".format(x, y, region_size))


if __name__ == "__main__":
    day11()
