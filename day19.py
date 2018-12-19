""" Solution to day 19 of the 2018 Advent of Code """

from utils import read_input, parse_args


def assign(registers, index, value):
    """ Assign a value to the register tuple, returning a new tuple """
    registers[index] = value
    return registers


def rop(registers, instruction, operation):
    """ Register operation """
    A, B, C = instruction
    A = registers[A]
    B = registers[B]
    return assign(registers, C, operation(A, B))


def iop(registers, instruction, operation):
    """ Immediate operation """
    A, B, C = instruction
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
    A, _, C = instruction
    A = registers[A]
    return assign(registers, C, A)


def seti(registers, instruction):
    """ (set immediate)
    stores value A into register C. (Input B is ignored.)
    """
    A, _, C = instruction
    return assign(registers, C, A)


def gtir(registers, instruction):
    """ (greater-than immediate/register)
    sets register C to 1 if value A is greater than register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction
    B = registers[B]
    value = 1 if A > B else 0
    return assign(registers, C, value)


def gtri(registers, instruction):
    """ (greater-than register/immediate)
    sets register C to 1 if register A is greater than value B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction
    A = registers[A]
    value = 1 if A > B else 0
    return assign(registers, C, value)


def gtrr(registers, instruction):
    """ (greater-than register/register)
    sets register C to 1 if register A is greater than register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction
    A = registers[A]
    B = registers[B]
    value = 1 if A > B else 0
    return assign(registers, C, value)


def eqir(registers, instruction):
    """ (equal immediate/register)
    sets register C to 1 if value A is equal to register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction
    B = registers[B]
    value = 1 if A == B else 0
    return assign(registers, C, value)


def eqri(registers, instruction):
    """ (equal register/immediate)
    sets register C to 1 if register A is equal to value B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction
    A = registers[A]
    value = 1 if A == B else 0
    return assign(registers, C, value)


def eqrr(registers, instruction):
    """ (equal register/register)
    sets register C to 1 if register A is equal to register B.
    Otherwise, register C is set to 0.
    """
    A, B, C = instruction
    A = registers[A]
    B = registers[B]
    value = 1 if A == B else 0
    return assign(registers, C, value)


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


def test(operation, instructions, registers, expected):
    """ Operation test """
    registers = list(registers)
    actual = tuple(operation(registers, instructions))
    assert actual == expected


def test_operations():
    """ Tests that all the operations work as expected """
    test(addr, (0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 8))
    test(addi, (3, 2, 1), (3, 5, 7, 11), (3, 13, 7, 11))

    test(mulr, (0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 15))
    test(muli, (3, 2, 1), (3, 5, 7, 11), (3, 22, 7, 11))

    test(banr, (0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 1))
    test(bani, (3, 2, 1), (3, 5, 7, 11), (3, 2, 7, 11))

    test(borr, (0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 7))
    test(bori, (3, 2, 1), (3, 5, 7, 11), (3, 11, 7, 11))

    test(setr, (0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 3))
    test(seti, (3, 2, 1), (3, 5, 7, 11), (3, 3, 7, 11))

    test(gtir, (0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 0))
    test(gtri, (3, 1, 2), (3, 5, 7, 11), (3, 5, 1, 11))
    test(gtrr, (2, 1, 0), (3, 5, 7, 11), (1, 5, 7, 11))

    test(eqir, (0, 1, 3), (3, 5, 7, 11), (3, 5, 7, 0))
    test(eqri, (3, 11, 2), (3, 5, 7, 11), (3, 5, 1, 11))
    test(eqrr, (2, 1, 0), (3, 5, 7, 11), (0, 5, 7, 11))


class CPU:
    """ Class representing the CPU """

    def __init__(self, registers=(0, 0, 0, 0, 0, 0)):
        self._registers = list(registers)
        self._ip = 0

    def run_program(self, program, verbose):
        """ Run a program on the CPU """
        self._ip = 0

        assert program[0].op_code == "#ip"
        binding = program[0].args[0]
        program = program[1:]

        while self._ip < len(program):
            inst = program[self._ip]
            if inst.op_code == "#ip":
                binding = inst.args[0]
                self._ip += 1
                continue

            if binding is not None:
                self._registers = assign(self._registers, binding, self._ip)

            if verbose:
                before = str(self._registers)

            self._registers = OPS[inst.op_code](self._registers, inst.args)
            if verbose:
                print("ip={}".format(self._ip), before, inst, self._registers)

            if binding is not None:
                self._ip = self._registers[binding]

            self._ip += 1

        return self._registers[0]


class Instruction:
    """ Class representing an instruction in a program """

    def __init__(self, line):
        parts = line.split()
        if parts[0].startswith("#"):
            self.op_code = "#ip"
            self.args = (int(parts[1].strip()), )
        else:
            self.op_code = parts[0]
            self.args = tuple([int(part.strip()) for part in parts[1:]])

        assert str(self) == line

    def __repr__(self):
        args = [str(arg) for arg in self.args]
        return "{} {}".format(self.op_code, " ".join(args))


def part1(program, verbose):
    """ Solution to part 1 """
    cpu = CPU()
    return cpu.run_program(program, verbose)


def part2(program, verbose):
    """ Solution to part 2 """
    cpu = CPU((1, 0, 0, 0, 0, 0))
    return cpu.run_program(program, verbose)


def day19():
    """ Solution to day 19 """
    args = parse_args()

    lines = read_input(19, args.debug).split("\n")
    program = [Instruction(line.strip()) for line in lines]

    print("Part 1")
    print(part1(program, args.verbose))

    print("Part 2")
    print(part2(program, args.verbose))


if __name__ == "__main__":
    day19()
