"""
detector.py


Author: GreeChel
"""


import cv2 as cv
import numpy as np
import json
import os
from matplotlib import pyplot as plt


def read_config():
    """
    A function that opens and outputs values from the config.json file
    Example:
    read_config("canny") -> {'key1': num1, 'key2', num2}
    """

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the config.json file
    config_path = os.path.join(script_dir, "config.json")

    # Read config.json -> data
    data = {}
    with open(config_path, 'r', encoding="utf-8") as f:
        data = json.load(f)

    # Output data
    return data


def find_candidates(img: np.ndarray):
    """
    A function that outputs a list of 3 taps - [x, y, r]
    """
    #
    config_data = read_config()

    # Convert image to GRAY
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Smuthing GRAY image with Gaussian blurring
    gauss_data = config_data["gaussian_blur"]
    gray_img = cv.GaussianBlur(gray_img,
                               ksize=(gauss_data["ksize"],
                                      gauss_data["ksize"]),
                               sigmaX=0)

    # Use algorithm Canny for selection (converting) faces
    canny_data = config_data["canny"]
    canny = cv.Canny(
        gray_img,
        threshold1=canny_data["threshold1"],
        threshold2=canny_data["threshold2"]
    )

    #
    hough_data = config_data["hough_circles"]
    circles = cv.HoughCircles(
        canny,
        method=cv.HOUGH_GRADIENT,
        dp=hough_data["dp"],
        minDist=hough_data["min_dist"],
        param1=hough_data["param1"],
        param2=hough_data["param2"],
        minRadius=hough_data["min_radius"],
        maxRadius=hough_data["max_radius"]
    )

    return circles


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
    img = cv.imread("detector/images/img1.jpg")
    print(find_candidates(img))
