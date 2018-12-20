""" Advent of code utilities """

import os
import argparse
from subprocess import Popen, PIPE, STDOUT

from PIL import Image, ImagePalette

PATH_TEMPLATE = "day{}_{}input.txt"


def read_input(day, debug=False):
    """ Read the input for a particular day """
    path = PATH_TEMPLATE.format(day, "debug_" if debug else "")
    path = os.path.join("inputs", path)
    with open(path) as file:
        return file.read()


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
    return parser.parse_args()


VIDEO_DIR = "videos"


class VideoBuilder:
    """ Build a video from colorized frame images """

    def __init__(self, path, sample_frame, color_map, frame_rate=24):
        if not os.path.exists(VIDEO_DIR):
            os.makedirs(VIDEO_DIR)

        height, width = sample_frame.shape
        if max(height, width) < 400:
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

        self._palette = ImagePalette.ImagePalette('RGB', red + green + blue, size*3)
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
