""" Solution to day 16 of the 2018 Advent of Code """

import logging
from collections import deque, namedtuple

from utils import read_input, parse_args
from cpu import OPS


def read_registers(line):
    """ Read the register state from a line """
    parts = line.strip(" []").split(',')
    return tuple([int(part) for part in parts])


def read_instruction(line):
    """ Read an instruction from a line """
    parts = line.strip().split()
    return tuple([int(part) for part in parts])


class Sample(namedtuple("Sample", ("index", "before", "args", "after"))):
    """ Class representing a register/instruction sample """

    @staticmethod
    def parse(lines):
        """ Parse a sample from the provided lines """
        assert len(lines) == 3
        assert lines[0].startswith("Before:")
        assert lines[2].startswith("After:")

        before = read_registers(lines[0][8:])
        spec = read_instruction(lines[1])
        index = spec[0]
        args = spec[1:]
        after = read_registers(lines[2][7:])
        return Sample(index, before, args, after)

    def find_matching_ops(self):
        """ Find all operations that match this sample """
        matches = []
        for code in OPS:
            registers = list(self.before)
            registers = tuple(OPS[code](registers, self.args))
            if registers == self.after:
                logging.debug(code)
                matches.append(code)

        return matches


def part1(samples):
    """ Solution to part 1 """
    num_matches = 0
    for sample in samples:
        matches = sample.find_matching_ops()
        if len(matches) >= 3:
            num_matches += 1

    return num_matches


def determine_op_codes(samples):
    """ Determine the correct sequence of op codes using the samples """
    op_indices = {}
    for code in OPS:
        op_indices[code] = set()

    for sample in samples:
        matches = sample.find_matching_ops()
        for match in matches:
            op_indices[match].add(sample.index)

    op_lookup = {}
    while op_indices:
        to_clear = []
        for code in op_indices:
            if len(op_indices[code]) == 1:
                op_lookup[code] = op_indices[code].pop()
                to_clear.append(code)

        for code in to_clear:
            del op_indices[code]
            index = op_lookup[code]
            for other_code in op_indices:
                if index in op_indices[other_code]:
                    op_indices[other_code].remove(index)

        logging.debug("%s %s", op_lookup, op_indices)

    op_codes = [""] * len(OPS)
    for code in op_lookup:
        op_codes[op_lookup[code]] = code

    logging.debug(op_codes)

    return op_codes


def part2(samples, program):
    """ Solution to part 2 """
    op_codes = determine_op_codes(samples)
    registers = [0, 0, 0, 0]
    for instruction in program:
        op_code = op_codes[instruction[0]]
        registers = OPS[op_code](registers, instruction[1:])

    return registers[0]


def day16():
    """ Solution to day 16 """
    parse_args()

    samples = []
    lines = deque(read_input(16))
    while lines[0].startswith("Before:"):
        sample = Sample.parse([
            lines.popleft(),
            lines.popleft(),
            lines.popleft()
        ])

        lines.popleft()

        samples.append(sample)

    print("Part 1")
    print(part1(samples))

    lines.popleft()
    lines.popleft()
    program = [read_instruction(line) for line in lines]

    print("Part 2")
    print(part2(samples, program))


if __name__ == "__main__":
    day16()
