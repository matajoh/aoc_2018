""" Instructions for the Elf CPU """

import pytest

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
