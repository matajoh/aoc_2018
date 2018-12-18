""" Advent of code utilities """

import os
import argparse
from subprocess import Popen, PIPE, STDOUT

import numpy as np
from PIL import Image

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

        self._color_map = color_map
        self._frame = np.zeros((height, width, 3), np.uint8)
        self._ffmpeg = Popen(['ffmpeg', '-y', '-f', 'image2pipe',
                              '-c:v', 'png',
                              '-s', "{}x{}".format(self._width, self._height),
                              '-pix_fmt', 'rgba',
                              '-framerate', str(frame_rate),
                              '-i', '-',
                              '-c:v', 'libx264',
                              '-b:v', '4M',
                              '-pix_fmt', 'yuv420p',
                              os.path.join(VIDEO_DIR, path)],
                             stdin=PIPE, stderr=STDOUT)

    def add_frame(self, state):
        """ Add a frame to the video using the state and the color map """
        for row, values in enumerate(state):
            for col, value in enumerate(values):
                self._frame[row, col] = self._color_map[value]

        with Image.fromarray(self._frame) as frame:
            if frame.width != self._width:
                frame = frame.resize((self._width, self._height))

            frame.save(self._ffmpeg.stdin, format='png')

    def close(self):
        """ Close the video """
        self._ffmpeg.stdin.close()
        self._ffmpeg.wait()
