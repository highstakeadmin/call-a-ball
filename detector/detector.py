#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""detector.py

A collection of functions to detect spherical uniformly-colored
markers (e.g., ping-pong balls) in photos and extract their
contours with sub-pixel accuracy.

Created by GreeChel on 16.06.2024
Updated by Alexey Pak on 16.06.2024
"""

import cv2 as cv
import numpy as np
import json, os
from matplotlib import pyplot as plt


def read_json(file_name):
    """Read a JSON file.

    Read a file and return its contents as a Python dict.

    Example:

    # A sample test.json:
    #   {
    #     "key1": 1.0,
    #     "key2": 'value'
    #   }

    cfg = read_config('test.json')

    # Result:
    #   cfg = {
    #     'key1': 1.0,
    #     'key2': 'value'
    #   }
    """

#    # Get the directory of the current script
#    script_dir = os.path.dirname(os.path.abspath(__file__))

#    # Construct the path to the config.json file
#    config_path = os.path.join(script_dir, "config.json")

    # Read config.json -> data
    data = {}
    with open(file_name, 'r', encoding="utf-8") as f:
        data = json.load(f)

    # Output data
    return data


def find_candidates(img: np.ndarray, config: dict):
    """Find circles in an image.

    Scan the provided RGB image using the Hough transform,
    find all objects with approximately circular contours.

    Sample config dict:

      config = {
        "find_candidates": {
          "canny": {
            "threshold1": 125,
            "threshold2": 96
          },
          "gaussian_blur": {
            "ksize": 5
          },
          "hough_circles": {
            "dp": 1,
            "min_dist": 600,
            "param1": 30,
            "param2": 17,
            "min_radius": 150,
            "max_radius": 230
          }
        }
      }

    Return a list of found candidates: [(x1, y1, r1), (x2, y2, r2), ...],
    where each candidate corresponds to a round object in the image,
    (x, y) is its center, and r is the radius. All values x, y, r are
    defined in terms of pixels.
    """

    # Convert image to grayscale.
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Smooth the image with Gaussian blurring.
    gauss_data = config["gaussian_blur"]
    gray_img = cv.GaussianBlur(
        gray_img,
        ksize=(gauss_data["ksize"],
        gauss_data["ksize"]),
        sigmaX=0)

    # Use the Canny algorithm to extract contours.
    canny_data = config["canny"]
    canny = cv.Canny(
        gray_img,
        threshold1=canny_data["threshold1"],
        threshold2=canny_data["threshold2"])

    # Use Hough transform to find circular contours.
    hough_data = config["hough_circles"]
    circles = cv.HoughCircles(
        canny,
        method=cv.HOUGH_GRADIENT,
        dp=hough_data["dp"],
        minDist=hough_data["min_dist"],
        param1=hough_data["param1"],
        param2=hough_data["param2"],
        minRadius=hough_data["min_radius"],
        maxRadius=hough_data["max_radius"])

    return circles


def show_candidates(img: np.ndarray, cands):
    """Visualize the output from find_candidates().

    In-paint the found candidates into the original
    image, display the image in an interactive window.
    """

    # Clone the image for modification.
    clone_img = img.copy()

    # Round the parameters of the found candidates.
    cands = np.uint16(np.around(cands))

    # Draw the circles.
    for (x, y, r) in cands:
        cv.circle(clone_img, (x, y), r, (0, 255, 0), 3)
        cv.circle(clone_img, (x, y), 3, (0, 255, 255), 5)

    # Show image with candidates
    cv.imshow("detected_circles", clone_img)
    cv.waitKey()


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
    config = read_json("config.json")
    img = cv.imread("detector/images/img1.jpg")

    cands = find_candidates(img, config["find_candidates"])
    show_candidates(img, cands)

    # data = read_config()
    # print(type(data["find_candidates"]))
