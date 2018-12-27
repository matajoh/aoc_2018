""" Solution to day 4 of the 2018 Advent of Code """

import logging
from datetime import datetime
from enum import Enum
from collections import namedtuple

import numpy as np

from utils import read_input, parse_args, assert_equal

FORMAT = "%Y-%m-%d %H:%M"


class EntryType(Enum):
    """ Enumeration of the types of log entries """
    Start = 0
    Wake = 1
    Sleep = 2


class LogEntry(namedtuple("LogEntry", ("time", "type", "guard"))):
    """ An entry in the guard log """

    @staticmethod
    def parse(line):
        """ Parse a log entry from the line """
        time = datetime.strptime(line[1:17], FORMAT)
        end = line[18:].strip()
        guard = None
        if end == "wakes up":
            entry_type = EntryType.Wake
        elif end == "falls asleep":
            entry_type = EntryType.Sleep
        else:
            entry_type = EntryType.Start
            parts = end.split()
            guard = int(parts[1][1:].strip())

        entry = LogEntry(time, entry_type, guard)
        assert_equal(str(entry), line)
        return entry

    def __lt__(self, other):
        return self.time < other.time

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


def sleepiest_guard(record, guards):
    """ Find the sleepliest guard is most likely to be asleep """
    sums = record.sum(axis=1)
    max_guard = np.argmax(sums)

    max_minute = np.argmax(record[max_guard])

    logging.debug("max_guard: %d", guards[max_guard])
    logging.debug("max_minute: %d", max_minute)
    return guards[max_guard] * max_minute


def most_consistently_sleepy_guard(record, guards):
    """ Find the guard who is most consistently asleep at the same time """
    max_index = np.argmax(record)
    max_guard, max_minute = np.unravel_index(max_index, [len(guards), 60])
    assert np.max(record) == record[max_guard, max_minute]
    logging.debug("max_guard: %d", guards[max_guard])
    logging.debug("max_minute: %d", max_minute)
    return guards[max_guard] * max_minute


def fill_in_guards(entries):
    """ Fill in the guard values for all entries """
    guards = set()
    guard = entries[0].guard
    for i, entry in enumerate(entries):
        if entry.type == EntryType.Start:
            guard = entry.guard
        else:
            entries[i] = LogEntry(entry.time, entry.type, guard)

        guards.add(entry.guard)

    return list(guards)


def create_record(entries, guards):
    """ Create a by-minute record for guard sleepiness """
    record = np.zeros((len(guards), 60), np.int32)

    guard_lookup = {
        guard: index for index, guard in enumerate(guards)
    }

    index = 0
    while index < len(entries):
        entry = entries[index]
        assert_equal(entry.type, EntryType.Start)
        guard = entry.guard
        row = guard_lookup[guard]
        index += 1
        while index < len(entries) and entries[index].type != EntryType.Start:
            assert_equal(entries[index].type, EntryType.Sleep)
            assert_equal(entries[index].guard, guard)
            start = entries[index].time.minute
            end = entries[index+1].time.minute
            index += 2
            for col in range(start, end):
                record[row, col] += 1

    return record


def day4():
    """ Solution to day 4 """
    parse_args()
    lines = read_input(4)
    entries = [LogEntry.parse(line) for line in lines]
    entries.sort()

    guards = fill_in_guards(entries)
    record = create_record(entries, guards)

    print("Part 1")
    print(sleepiest_guard(record, guards))

    print("Part 2")
    print(most_consistently_sleepy_guard(record, guards))


if __name__ == "__main__":
    day4()
