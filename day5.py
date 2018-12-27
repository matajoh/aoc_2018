""" Solution to day 5 of the 2018 Advent of Code """

from utils import read_input

# TODO rewrite to use linked lists

def reduce(polymer, reduced):
    """ Reduce the polymer following the rules """
    current_element = None
    for next_element in polymer:
        if current_element is None:
            current_element = next_element
        else:
            if current_element.lower() == next_element.lower():
                if current_element == next_element:
                    reduced.append(current_element)
                else:
                    current_element = None
            else:
                reduced.append(current_element)
                current_element = next_element

    if current_element is not None:
        reduced.append(current_element)

    return reduced


def react(polymer):
    """ Fully react the polymer and return the final length """
    length = len(polymer)
    reduced = []
    while True:
        reduce(polymer, reduced)
        polymer, reduced = reduced, polymer
        reduced.clear()
        if len(polymer) == length:
            break

        length = len(polymer)

    return length


def part1(polymer):
    """ Solution to part 1 """
    print(react(list(polymer)))


def part2(original_polymer):
    """ Solution to part 2 """
    unique_elements = set(original_polymer.lower())
    min_length = len(original_polymer)
    for element in unique_elements:
        polymer = list(filter(lambda unit, compare=element: unit.lower()
                              != compare, original_polymer))
        length = react(polymer)
        if length < min_length:
            min_length = length
        print(element, length)

    print("min length:", min_length)


def day5():
    """ Solution to day 5 """
    polymer = read_input(5, no_split=True)
    print("Part 1")
    part1(polymer)
    print("Part 2")
    part2(polymer)


if __name__ == "__main__":
    day5()
