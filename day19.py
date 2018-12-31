""" Solution to day 19 of the 2018 Advent of Code """

import numpy as np

from utils import read_input, parse_args
from cpu import CPU, Instruction


def simulate(program):
    """ Simulate the CPU on the instruction stack """
    cpu = CPU()
    cpu.run_program(program)
    return cpu.stack[0]


def decompiled(longer_version):
    """ Decompiled (and optimized) version of the instruction set """
    product = 950
    if longer_version:
        product += 10550400

    result = 0
    limit = int(np.sqrt(product)) + 1  # optimization
    for i in range(0, limit):
        factor = i + 1
        if product % factor == 0:
            result += product // factor  # optimization
            result += factor

    return result


def test_day19():
    """ Test for day 19 """
    lines = read_input(19, True)
    program = [Instruction(line) for line in lines]
    cpu = CPU()
    cpu.run_program(program)

    expected = 6
    actual = cpu.stack[0]
    assert actual == expected


def day19():
    """ Solution to day 19 """
    parse_args()

    lines = read_input(19)
    program = [Instruction(line.strip()) for line in lines]

    print("Part 1")
    expected = simulate(program)
    actual = decompiled(False)
    print("Simulation:", expected, "Decompiled:", actual)

    print("Part 2")
    print("Decompiled:", decompiled(True))


if __name__ == "__main__":
    day19()
