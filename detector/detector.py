import cv2 as cv
import numpy as np
import json


def read_config(name: str):
    """
    A function that opens and outputs values from the config.json file
    Example:
    read_config("canny") -> {'key1': num1, 'key2', num2}
    """

    # Read config.json -> data
    data = {}
    with open("config.json", 'r', encoding="utf-8") as f:
        data = json.load(f)

    # Output data[name]
    return data[name]


def find_candidates(img: np.ndarray):
    """
    A function that outputs a list of 3 taps - [x, y, r]
    """
    # Convert image to GRAY


def show_candidates(img, cands):
    """
    shows the picture where find_candidates was found
    """
    pass


def find_targets(img, cands):
    pass


def show_targets(img, targs):
    pass


def find_contours(img, targ):
    pass


def show_contours(pmap):
    pass


# Entry point for quick tests
if __name__ == "__main__":
    data = read_config("canny")
    print(data)
