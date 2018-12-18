import numpy as np
from PIL import Image

COLORS = {
    '.': (0, 0, 0),
    '#': (255, 0, 0),
    '|': (0, 255, 255),
    '~': (0, 0, 255),
    '+': (255, 255, 255),
    '$': (0, 0, 128)
}

def main():
    in_file = "ground.txt"
    out_file = in_file.replace(".txt", ".png")
    with open(in_file) as file:
        lines = file.read().split('\n')
    
    rows = len(lines)
    cols = len(lines[0])

    start_counting = False
    num_reachable = 0
    num_water = 0
    pixels = np.zeros((rows, cols, 3), np.uint8)
    for row in range(rows):
        for col in range(cols):
            char = lines[row][col]
            if not start_counting and char == '#':
                start_counting = True

            if start_counting and char in ('~', '|', '$'):
                num_reachable += 1
                if char != '|':
                    num_water += 1

            assert char in COLORS, "{},{}: {}".format(row, col, char)
            pixels[row, col] = COLORS[lines[row][col]]

    print("Reachable:", num_reachable)
    print("At rest:", num_water)
    image = Image.fromarray(pixels)
    image.save(out_file)

if __name__ == "__main__":
    main()
