""" Advent of code utilities """

import os
import argparse

PATH_TEMPLATE = "day{}_{}input.txt"

def read_input(day, debug=False):
    """ Read the input for a particular day """
    path = PATH_TEMPLATE.format(day, "debug_" if debug else "")
    path = os.path.join("inputs", path)
    with open(path) as file:
        return file.read()

def parse_args():
    """ Parse argument from the command line """

    parser = argparse.ArgumentParser("Advent of Code")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()
