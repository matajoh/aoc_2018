""" Solution to day 7 of the 2018 Advent of Code """

import heapq

from utils import read_input, parse_args


DEBUG = (
    "Step C must be finished before step A can begin.\n"
    "Step C must be finished before step F can begin.\n"
    "Step A must be finished before step B can begin.\n"
    "Step A must be finished before step D can begin.\n"
    "Step B must be finished before step E can begin.\n"
    "Step D must be finished before step E can begin.\n"
    "Step F must be finished before step E can begin."
)


class Step:
    """ Class encapsulating a step in the construction process """

    def __init__(self, name, base_time):
        self.name = name
        self.time = (ord(name) - ord('A') + 1) + base_time
        self.num_complete = 0
        self.parents = []
        self.children = []

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


def part1(step_lookup):
    """ Solution to part 1 """
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

    print("".join(order))


def part2(step_lookup, num_workers):
    """ Solution to part 2 """
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
        parts = [step.name for step in current_steps]
        parts = [num_seconds] + parts + ["".join(order)]
        print(*parts)

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

    print("".join(order))
    print(num_seconds)


def day7(debug):
    """ Solution to day 7 """

    if debug:
        lines = DEBUG.split('\n')
        base_time = 0
        num_workers = 2
    else:
        lines = read_input(7).split('\n')
        base_time = 60
        num_workers = 5

    step_lookup = {}
    for line in lines:
        add_edge(step_lookup, line, base_time)

    print("Part 1")
    part1(step_lookup)

    step_lookup = {}
    for line in lines:
        add_edge(step_lookup, line, base_time)

    print("Part 2")
    part2(step_lookup, num_workers)


if __name__ == "__main__":
    ARGS = parse_args()
    day7(ARGS.debug)
