""" Advent of code utilities """

import os
import argparse
import itertools
import logging
import heapq
from collections import deque
from subprocess import Popen, PIPE, STDOUT

from PIL import Image, ImagePalette, ImageDraw, ImageFont
import numpy as np

PATH_TEMPLATE = "day{}_{}input.txt"


def read_input(day, test=False, no_split=False):
    """ Read the input for a particular day """
    path = PATH_TEMPLATE.format(day, "test_" if test else "")
    path = os.path.join("inputs", path)
    with open(path) as file:
        contents = file.read()
        if no_split:
            return contents

        return [line.strip() for line in contents.split('\n')]


TEMP_DIR = "temp"


def temp_file(path):
    """ Return a path to a temporary file """
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    return os.path.join(TEMP_DIR, path)


def parse_args():
    """ Parse argument from the command line """

    parser = argparse.ArgumentParser("Advent of Code")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--video", action="store_true")
    parser.add_argument("--num_video_frames", type=int, default=0)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            format='%(levelname)s: %(message)s', level=logging.DEBUG)

    return args


VIDEO_DIR = "videos"


class VideoBuilder:
    """ Build a video from colorized frame images """

    def __init__(self, path, sample_state, color_map, frame_rate=24, no_resize=False):
        if not os.path.exists(VIDEO_DIR):
            os.makedirs(VIDEO_DIR)

        height, width = sample_state.shape
        if max(height, width) < 400 and not no_resize:
            if height > width:
                self._height = 400
                self._width = (400*width)//height
            else:
                self._width = 400
                self._height = (400*height)//width
        else:
            self._width, self._height = width, height

        size = max(color_map.keys()) + 1
        red = [0] * size
        green = [0] * size
        blue = [0] * size
        for key in color_map:
            red[key], green[key], blue[key] = color_map[key]

        self._palette = ImagePalette.ImagePalette(
            'RGB', red + green + blue, size*3)
        self._ffmpeg = Popen(['ffmpeg', '-y', '-f', 'image2pipe',
                              '-c:v', 'png',
                              '-s', "{}x{}".format(self._width, self._height),
                              '-framerate', str(frame_rate),
                              '-i', '-',
                              '-c:v', 'libx264',
                              '-b:v', '4M',
                              '-pix_fmt', 'yuv420p',
                              os.path.join(VIDEO_DIR, path)],
                             stdin=PIPE, stderr=STDOUT)

    def add_frame(self, state):
        """ Add a frame to the video using the state and the color map """
        with Image.fromarray(state, 'P') as frame:
            frame.putpalette(self._palette)
            if frame.width != self._width:
                frame = frame.resize((self._width, self._height))

            frame.save(self._ffmpeg.stdin, format='png')

    def close(self):
        """ Close the video """
        self._ffmpeg.stdin.close()
        self._ffmpeg.wait()


class ASCIIVideoBuilder(VideoBuilder):
    """ Video Builder which uses ASCII characters instead of pixels """

    def __init__(self, path, sample_state, color_map, frame_rate=24):
        font = ImageFont.load_default()
        size = font.getsize("a")
        self._glyph_cols, self._glyph_rows = size
        self._glyphs = {}
        for code in color_map:
            image = Image.new('L', size)
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), chr(code), fill=code, font=font)
            self._glyphs[code] = np.array(image)

        rows, cols = sample_state.shape
        rows *= self._glyph_rows
        cols *= self._glyph_cols
        self._glyph_state = np.zeros((rows, cols), np.uint8)
        super().__init__(path, self._glyph_state, color_map, frame_rate, True)

    def add_frame(self, state):
        rows, cols = state.shape
        for row in range(rows):
            top = row * self._glyph_rows
            bottom = top + self._glyph_rows
            for col in range(cols):
                left = col * self._glyph_cols
                right = left + self._glyph_cols
                glyph = self._glyphs[state[row, col]]
                self._glyph_state[top:bottom, left:right] = glyph

        super().add_frame(self._glyph_state)


class Point:
    """ Class representing a point """

    def __init__(self, row, col):
        self._row = row
        self._col = col
        self._hash = (row, col).__hash__()

    def __eq__(self, other):
        return not (self.row != other.row or self.col != other.col)

    def __hash__(self):
        return self._hash

    def __getitem__(self, key):
        if key == 0:
            return self._row

        if key == 1:
            return self._col

        raise IndexError("Invalid index")

    def __len__(self):
        return 2

    def __repr__(self):
        return "{}(row={}, col={})".format(type(self).__name__, self._row, self._col)

    @property
    def row(self):
        """ The row value """
        return self._row

    @property
    def col(self):
        """ The column value """
        return self._col

    def __add__(self, other):
        return Point(self._row + other.row, self._col + other.col)


def assert_equal(actual, expected):
    """ Assert the two values are equal, and print an appropriate error message """
    if isinstance(actual, str):
        assert actual == expected, diff(actual, expected)

    assert actual == expected, "{} != {}".format(actual, expected)


def diff(actual, expected):
    """ Returns the diff between two multi-line strings """
    actual_lines = actual.split('\n')
    expected_lines = expected.split('\n')

    if len(actual_lines) != len(expected_lines):
        return "Line count differs: {} != {}".format(len(actual_lines),
                                                     len(expected_lines))

    result = ["\n" + actual]
    for line, (actual_line, expected_line) in enumerate(zip(actual_lines,
                                                            expected_lines)):
        if len(actual_line) != len(expected_line):
            print("{}: length differs: {} != {}".format(
                line,
                len(actual_line),
                len(expected_line)))
        else:
            diffs = []
            for actual_char, expected_char in zip(actual_line, expected_line):
                if actual_char != expected_char:
                    diffs.append('X')
                else:
                    diffs.append('.')

            result.append(diffs)

    return "\n".join(["".join(line) for line in result])


class AStarSearch:
    """ Implementation of A* Search """

    def __init__(self, heuristic, distance_between, graph):
        self._heuristic = heuristic
        self._distance_between = distance_between
        self._graph = graph

    @staticmethod
    def _reconstruct_path(came_from, current):
        """ Reconstructs a path for A* search """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)

        return total_path

    def find_shortest_path(self, start, goal):
        """ Find the shortest path from the start to the goal """
        closed_set = set()
        open_set = PriorityQueue()
        open_set.add(start, self._heuristic(start, goal))
        came_from = {}
        g_scores = {}
        g_scores[start] = 0
        iteration = 0
        while open_set:
            f_score, current = open_set.pop()

            iteration += 1
            if iteration % 100 == 0:
                logging.debug("%d: |open_set|=%d current f score: %d",
                              iteration, len(open_set), f_score)

            if current == goal:
                return AStarSearch._reconstruct_path(came_from, current)

            closed_set.add(current)

            for neighbor in self._graph.neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_scores[current]
                tentative_g_score += self._distance_between(current, neighbor)
                if neighbor in open_set:
                    if tentative_g_score >= g_scores[neighbor]:
                        continue

                came_from[neighbor] = current
                g_scores[neighbor] = tentative_g_score

                f_score = g_scores[neighbor] + self._heuristic(neighbor, goal)
                open_set.add(neighbor, f_score)

        return None


class MaxClique:
    """ Find the maximum clique in a graph """

    def __init__(self, edges, verbose):
        self._edges = edges
        self._current = []
        self._max = []
        self._max_size = 0
        self._verbose = verbose

    def _find_color_groups(self, nodes):
        color_groups = []
        for node in nodes:
            adjacent = True
            for color_group in color_groups:
                if np.sum(self._edges[node][color_group]) == 0:
                    color_group.append(node)
                    adjacent = False
                    break

            if adjacent:
                color_groups.append([node])

        return color_groups

    def _color_graph(self, nodes):
        if self._verbose:
            print("coloring graph of size", len(nodes))

        color_groups = self._find_color_groups(nodes)
        nodes = []
        colors = []
        for color, color_group in enumerate(color_groups):
            nodes.extend(color_group)
            colors.extend([color + 1] * len(color_group))

        return nodes, colors

    def find(self):
        """ Finds the maximum clique """
        nodes = list(range(self._edges.shape[0]))
        self._max_clique(nodes)
        return self._max

    def _max_clique(self, nodes):
        if self._verbose:
            print("finding max clique for graph of size", len(nodes))

        nodes, colors = self._color_graph(nodes)

        while nodes:
            node = nodes.pop()
            color = colors.pop()
            if self._verbose:
                print("|Q| + C = ", len(self._current) +
                      color, "|Qmax| = ", self._max_size)

            if len(self._current) + color >= self._max_size:
                self._current.append(node)
                adjacent = []
                for other in nodes:
                    if self._edges[node, other]:
                        adjacent.append(other)

                if adjacent:
                    self._max_clique(adjacent)
                elif len(self._current) > self._max_size:
                    self._max_size = len(self._current)
                    self._max = [self._current.copy()]
                elif len(self._current) == self._max_size:
                    self._max.append(self._current.copy())

                assert self._current.pop() == node
            else:
                return


class PriorityQueue:
    """ Implementation of a priority queue """
    REMOVED = '<removed-value>'

    def __init__(self):
        self._entries = []
        self._entry_finder = {}
        self._counter = itertools.count()

    def __len__(self):
        return len(self._entries)

    def __contains__(self, value):
        return value in self._entry_finder

    def add(self, value, priority=0):
        """ Add a new value or update the priority of an existing value """
        if value in self._entry_finder:
            self._remove_value(value)

        count = next(self._counter)
        entry = [priority, count, value]
        self._entry_finder[value] = entry
        heapq.heappush(self._entries, entry)

    def _remove_value(self, value):
        """Mark an existing task as REMOVED.  Raise KeyError if not found."""
        entry = self._entry_finder.pop(value)
        entry[-1] = PriorityQueue.REMOVED

    def pop(self):
        """Remove and return the lowest priority task. Raise KeyError if empty."""
        while self._entries:
            priority, _, value = heapq.heappop(self._entries)
            if value is not PriorityQueue.REMOVED:
                del self._entry_finder[value]
                return priority, value
        raise KeyError('pop from an empty priority queue')


class Tokenizer:
    """ Tokenizes a string and provides useful parsing abilities """

    def __init__(self, text):
        self.tokens = deque(text)

    def peek(self):
        """ Returns the current token without consuming it """
        if self.tokens:
            return self.tokens[0]

        return None

    def read(self, num_tokens=1):
        """ Read and consumes at most `num_tokens` from the string """
        result = []
        for _ in range(num_tokens):
            if self.tokens:
                result.append(self.tokens.popleft())

        return "".join(result)

    def consume(self, expected):
        """ Consumes and asserts the tokens in the string """
        actual = self.read(len(expected))
        assert actual == expected, diff(actual, expected)

    def skip_whitespace(self):
        """ Consumes whitespace tokens until non-whitespace is encountered """
        while self.peek() and self.peek().isspace():
            self.read()

    def read_word(self):
        """ Reads a sequence of alpha characters"""
        result = []
        self.skip_whitespace()
        while self.peek():
            if not self.peek().isalpha():
                break

            result.append(self.read())

        return "".join(result)

    def read_until(self, *args):
        """ Reads tokens until the provided arguments are encountered """
        result = []
        assert args
        stop = set(args)
        while self.peek() and self.peek() not in stop:
            result.append(self.read())

        return "".join(result)

    def read_int(self):
        """ Reads an integer """
        result = []
        self.skip_whitespace()
        while self.peek():
            if self.peek().isspace():
                break

            if self.peek().isdigit():
                result.append(self.read())
            else:
                break

        return int("".join(result))
