""" Solution to day 16 of the 2018 Advent of Code """

import logging
from collections import deque

import pytest

from utils import read_input, parse_args


def assign(registers, index, value):
    """ Assign a value to the register tuple, returning a new tuple """
    registers = list(registers)
    registers[index] = value
    return tuple(registers)


def rop(registers, instruction, operation):
    """ Register operation """
    A, B, C = instruction[1:]
    A = registers[A]
    B = registers[B]
    return assign(registers, C, operation(A, B))


def iop(registers, instruction, operation):
    """ Immediate operation """
    A, B, C = instruction[1:]
    A = registers[A]
    return assign(registers, C, operation(A, B))


def addr(registers, instruction):
    """ (add register)
    stores into register C the result of adding register A and register B.
    """
    return rop(registers, instruction, lambda a, b: a + b)


def addi(registers, instruction):
    """ (add immediate)
    stores into register C the result of adding register A and value B.
    """
    return iop(registers, instruction, lambda a, b: a + b)


def mulr(registers, instruction):
    """ (multiply register)
    stores into register C the result of multiplying register A and register B.
    """
    return rop(registers, instruction, lambda a, b: a*b)


def muli(registers, instruction):
    """ (multiply immediate)
    stores into register C the result of multiplying register A and value B.
    """
    return iop(registers, instruction, lambda a, b: a*b)


def banr(registers, instruction):
    """ (bitwise AND register)
    stores into register C the result of the bitwise AND of register A and register B.
    """
    return rop(registers, instruction, lambda a, b: a & b)


def bani(registers, instruction):
    """(bitwise AND immediate)
    stores into register C the result of the bitwise AND of register A and value B.
    """
    return iop(registers, instruction, lambda a, b: a & b)


def borr(registers, instruction):
    """ (bitwise OR register)
    stores into register C the result of the bitwise OR of register A and register B.
    """
    return rop(registers, instruction, lambda a, b: a | b)


def bori(registers, instruction):
    """ (bitwise OR immediate)
    stores into register C the result of the bitwise OR of register A and value B.
    """
    return iop(registers, instruction, lambda a, b: a | b)


def setr(registers, instruction):
    """ (set register)
    copies the contents of register A into register C. (Input B is ignored.)
    """
    A, _, C = instruction[1:]
    A = registers[A]
    return assign(registers, C, A)


def seti(registers, instruction):
    """ (set immediate)
    stores value A into register C. (Input B is ignored.)
    """
    A, _, C = instruction[1:]
    return assign(registers, C, A)


def gtir(registers, instruction):
    """ (greater-than immediate/register)
    sets register C to 1 if value A is greater than register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction[1:]
    B = registers[B]
    value = 1 if A > B else 0
    return assign(registers, C, value)


def gtri(registers, instruction):
    """ (greater-than register/immediate)
    sets register C to 1 if register A is greater than value B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction[1:]
    A = registers[A]
    value = 1 if A > B else 0
    return assign(registers, C, value)


def gtrr(registers, instruction):
    """ (greater-than register/register)
    sets register C to 1 if register A is greater than register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction[1:]
    A = registers[A]
    B = registers[B]
    value = 1 if A > B else 0
    return assign(registers, C, value)


def eqir(registers, instruction):
    """ (equal immediate/register)
    sets register C to 1 if value A is equal to register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction[1:]
    B = registers[B]
    value = 1 if A == B else 0
    return assign(registers, C, value)


def eqri(registers, instruction):
    """ (equal register/immediate)
    sets register C to 1 if register A is equal to value B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction[1:]
    A = registers[A]
    value = 1 if A == B else 0
    return assign(registers, C, value)


def eqrr(registers, instruction):
    """ (equal register/register)
    sets register C to 1 if register A is equal to register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction[1:]
    A = registers[A]
    B = registers[B]
    value = 1 if A == B else 0
    return assign(registers, C, value)


OP_TESTS = [
    (addr, (None, 0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 8)),
    (addi, (None, 3, 2, 1), (3, 5, 7, 11), (3, 13, 7, 11)),

    (mulr, (None, 0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 15)),
    (muli, (None, 3, 2, 1), (3, 5, 7, 11), (3, 22, 7, 11)),

    (banr, (None, 0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 1)),
    (bani, (None, 3, 2, 1), (3, 5, 7, 11), (3, 2, 7, 11)),

    (borr, (None, 0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 7)),
    (bori, (None, 3, 2, 1), (3, 5, 7, 11), (3, 11, 7, 11)),

    (setr, (None, 0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 3)),
    (seti, (None, 3, 2, 1), (3, 5, 7, 11), (3, 3, 7, 11)),

    (gtir, (None, 0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 0)),
    (gtri, (None, 3, 1, 2), (3, 5, 7, 11), (3, 5, 1, 11)),
    (gtrr, (None, 2, 1, 0), (3, 5, 7, 11), (1, 5, 7, 11)),

    (eqir, (None, 0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 0)),
    (eqri, (None, 3, 11, 2), (3, 5, 7, 11), (3, 5, 1, 11)),
    (eqrr, (None, 2, 1, 0), (3, 5, 7, 11), (0, 5, 7, 11)),
]

OPS = {
    "addr": addr,
    "addi": addi,
    "mulr": mulr,
    "muli": muli,
    "banr": banr,
    "bani": bani,
    "borr": borr,
    "bori": bori,
    "setr": setr,
    "seti": seti,
    "gtir": gtir,
    "gtri": gtri,
    "gtrr": gtrr,
    "eqir": eqir,
    "eqri": eqri,
    "eqrr": eqrr
}


@pytest.mark.parametrize("operation, instructions, registers, expected", OP_TESTS)
def test_operation(operation, instructions, registers, expected):
    """ Operation test """
    assert operation(registers, instructions) == expected


def read_registers(line):
    """ Read the register state from a line """
    parts = line.strip(" []").split(',')
    return tuple([int(part) for part in parts])


def read_instruction(line):
    """ Read an instruction from a line """
    parts = line.strip().split()
    return tuple([int(part) for part in parts])


class Sample:
    """ Class representing a register/instruction sample """

    def __init__(self, lines, index):
        assert len(lines) == 3
        assert lines[0].startswith("Before:")
        assert lines[2].startswith("After:")

        self.index = index
        self.before = read_registers(lines[0][8:])
        self.instruction = read_instruction(lines[1])
        self.after = read_registers(lines[2][7:])

    def find_matching_ops(self):
        """ Find all operations that match this sample """
        matches = []
        for code in OPS:
            if OPS[code](self.before, self.instruction) == self.after:
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
            op_indices[match].add(sample.instruction[0])

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
    registers = (0, 0, 0, 0)
    for instruction in program:
        op_code = op_codes[instruction[0]]
        registers = OPS[op_code](registers, instruction)

    return registers[0]


def day16():
    """ Solution to day 16 """
    parse_args()

    samples = []
    lines = deque(read_input(16))
    index = 0
    while lines[0].startswith("Before:"):
        sample = Sample([
            lines.popleft(),
            lines.popleft(),
            lines.popleft()
        ], index)
        index += 1

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
