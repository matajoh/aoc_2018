""" Solution to day 7 of the 2018 Advent of Code """

import heapq
import logging

from utils import read_input, parse_args


TEST = [
    "Step C must be finished before step A can begin.",
    "Step C must be finished before step F can begin.",
    "Step A must be finished before step B can begin.",
    "Step A must be finished before step D can begin.",
    "Step B must be finished before step E can begin.",
    "Step D must be finished before step E can begin.",
    "Step F must be finished before step E can begin."
]


class Step:
    """ Class encapsulating a step in the construction process """

    def __init__(self, name, base_time):
        self.name = name
        self.time = (ord(name) - ord('A') + 1) + base_time
        self.num_complete = 0
        self.parents = []
        self.children = []

    def reset(self):
        """ Reset the task """
        self.num_complete = 0

    def complete(self):
        """ Complete the step, notifying children """
        for step in self.children:
            step.num_complete += 1

    def is_ready(self):
        """ Tests whether the step is ready to begin """
        return self.num_complete == len(self.parents)

    def __lt__(self, other):
        return self.name < other.name


def add_edge(steps, line, base_time):
    """ Adds an edge to the step dependency graph """
    key0 = line[5]
    key1 = line[36]
    if key0 not in steps:
        steps[key0] = Step(key0, base_time)

    if key1 not in steps:
        steps[key1] = Step(key1, base_time)

    steps[key0].children.append(steps[key1])
    steps[key1].parents.append(steps[key0])


def build_step_lookup(lines, base_time):
    """ Build the step lookup dictionary """
    step_lookup = {}
    for line in lines:
        add_edge(step_lookup, line, base_time)

    return step_lookup


def find_order_of_instructions(step_lookup):
    """ Find the order in which the instructions should be completed """
    unready = list(step_lookup.keys())
    order = []
    steps = []

    for step in step_lookup.values():
        if step.is_ready():
            heapq.heappush(steps, step.name)
            unready.remove(step.name)

    while steps:
        step_name = heapq.heappop(steps)
        order.append(step_name)
        step = step_lookup[step_name]
        step.complete()
        update = []
        for name in unready:
            if step_lookup[name].is_ready():
                heapq.heappush(steps, name)
            else:
                update.append(name)

        unready = update

    return "".join(order)


def compute_duration(step_lookup, num_workers):
    """ Determine how long it will take to complete the task. """
    unready = list(step_lookup.keys())
    order = []
    steps = []
    current_steps = []

    for step in step_lookup.values():
        if step.is_ready():
            heapq.heappush(steps, step.name)
            unready.remove(step.name)

    while steps and len(current_steps) < num_workers:
        step = step_lookup[heapq.heappop(steps)]
        current_steps.append(step)

    num_seconds = 0
    while steps or current_steps:
        logging.debug("%d %s %s",
                      num_seconds,
                      " ".join([step.name for step in current_steps]),
                      "".join(order))

        num_seconds += 1
        for step in current_steps:
            step.time -= 1
            assert step.time >= 0

        complete = list(filter(lambda step: step.time == 0, current_steps))
        for step in complete:
            step.complete()
            current_steps.remove(step)
            order.append(step.name)

        update = []
        for name in unready:
            if step_lookup[name].is_ready():
                heapq.heappush(steps, name)
            else:
                update.append(name)

        unready = update

        while len(current_steps) < num_workers and steps:
            step = step_lookup[heapq.heappop(steps)]
            current_steps.append(step)

    logging.debug("".join(order))
    return num_seconds


def test_day7():
    """ Test for day 7 """

    lines = TEST
    base_time = 0
    num_workers = 2
    step_lookup = build_step_lookup(lines, base_time)

    expected = "CABDFE"
    actual = find_order_of_instructions(step_lookup)
    assert actual == expected

    for step in step_lookup.values():
        step.reset()

    expected = 15
    actual = compute_duration(step_lookup, num_workers)
    assert actual == expected


def day7():
    """ Solution to day 7 """
    parse_args()

    lines = read_input(7)
    base_time = 60
    num_workers = 5

    step_lookup = build_step_lookup(lines, base_time)

    print("Part 1")
    print(find_order_of_instructions(step_lookup))

    for step in step_lookup.values():
        step.reset()

    print("Part 2")
    print(compute_duration(step_lookup, num_workers))


if __name__ == "__main__":
    day7()
