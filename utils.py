""" Advent of code utilities """

import os

PATH_TEMPATE = "day{}_input.txt"

def read_input(day):
    """ Read the input for a particular day """
    path = os.path.join("inputs", PATH_TEMPATE.format(day))
    with open(path) as file:
        return file.read()
