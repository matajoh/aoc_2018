""" Solution to day 21 of the 2018 Advent of Code """

import logging

from utils import parse_args


def decompiled(num_checks):
    """ Decompiled (and optimized) version of the instruction set """
    a = 0
    a_values = set()
    checks = []
    while True:
        b = a | 0x10000
        a = 1765573

        while b > 0:
            a = a + (b & 0xFF)
            a = a & 0xFFFFFF
            a = a * 65899
            a = a & 0xFFFFFF
            b = b >> 8

        logging.debug("%d %d", len(checks), a)

        if num_checks and len(checks) == num_checks:
            logging.debug("all checks found")
            break

        if a not in a_values:
            a_values.add(a)
            checks.append(a)
        else:
            break

    return checks


def day21():
    """ Solution to day 21 """
    parse_args()

    print("Part 1")
    checks = decompiled(1)
    print(checks[0])

    print("Part 2")
    checks = decompiled(None)
    print(checks[-1])


if __name__ == "__main__":
    day21()
