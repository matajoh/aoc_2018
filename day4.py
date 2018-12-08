""" Solution to day 4 of the 2018 Advent of Code """

from datetime import datetime
from enum import Enum
import numpy as np
from utils import read_input

FORMAT = "%Y-%m-%d %H:%M"


class EntryType(Enum):
    """ Enumeration of the types of log entries """
    Start = 0
    Wake = 1
    Sleep = 2


class LogEntry:
    """ An entry in the guard log """

    def __init__(self, line):
        line = line.strip()
        self.time = datetime.strptime(line[1:17], FORMAT)
        end = line[18:].strip()
        self.guard = None
        if end == "wakes up":
            self.type = EntryType.Wake
        elif end == "falls asleep":
            self.type = EntryType.Sleep
        else:
            self.type = EntryType.Start
            parts = end.split()
            self.guard = int(parts[1][1:].strip())

        assert line == str(self), line + " != " + str(self)

    def __repr__(self):
        if self.type == EntryType.Wake:
            end = "wakes up"
        elif self.type == EntryType.Sleep:
            end = "falls asleep"
        else:
            end = "Guard #{} begins shift".format(self.guard)

        return "[{}] {}".format(
            self.time.strftime(FORMAT),
            end
        )


def part1(record, guards):
    """ Solution to part 1 """
    sums = record.sum(axis=1)
    max_guard = np.argmax(sums)

    max_minute = np.argmax(record[max_guard])

    print("max_guard:", guards[max_guard])
    print("max_minute:", max_minute)
    print("result:", guards[max_guard] * max_minute)


def part2(record, guards):
    """ Solution to part 2 """
    max_index = np.argmax(record)
    max_guard, max_minute = np.unravel_index(max_index, [len(guards), 60])
    assert np.max(record) == record[max_guard, max_minute]
    print("max_guard:", guards[max_guard])
    print("max_minute:", max_minute)
    print("result:", guards[max_guard] * max_minute)


def day4():
    """ Solution to day 4 """
    lines = read_input(4).split('\n')
    entries = [LogEntry(line) for line in lines]
    entries.sort(key=lambda entry: entry.time)
    guards = set()
    guard = entries[0].guard
    for entry in entries:
        if entry.type == EntryType.Start:
            guard = entry.guard
        else:
            entry.guard = guard

        guards.add(entry.guard)

    guards = list(guards)

    guard_lookup = {
        guard: index for index, guard in enumerate(guards)
    }

    record = np.zeros((len(guards), 60), np.int32)

    index = 0
    while index < len(entries):
        entry = entries[index]
        assert entry.type == EntryType.Start, "{} != Start @ {}".format(
            entry.type, index)
        guard = entry.guard
        row = guard_lookup[guard]
        index += 1
        while index < len(entries) and entries[index].type != EntryType.Start:
            assert entries[index].type == EntryType.Sleep, "{} != Sleep @ {}".format(
                entry.type, index)
            assert entries[index].guard == guard, "{} != {} @ {}".format(
                entry.guard, guard, index)
            start = entries[index].time.minute
            end = entries[index+1].time.minute
            index += 2
            for col in range(start, end):
                record[row, col] += 1

    print("Part 1")
    part1(record, guards)

    print("Part 2")
    part2(record, guards)


if __name__ == "__main__":
    day4()
