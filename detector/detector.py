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
<<<<<<< HEAD
import json, os
=======
import json
import os
import math
>>>>>>> b3dbfba (Update detector.py for find_candidates())
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit


def gauss_f(x, A, mu, sig):
    return A*np.exp(-(x-mu)**2/sig**2)


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


def write_config(config: dict, key: str):
    """
    Function for writing optimaze parameters to config file in config.json
    """
    pass


def optimaze_gaussian_blur(img: np.ndarray, config: dict):
    """
    Adjust the configuration parameters of cv.GaussianBlur() function
    by triggers
    """
    pass


def optimaze_canny(img: np.ndarray, config: dict):
    """
    Adjust the configuration parameters of cv.Canny() function
    by triggers
    """
    pass


def optimize_hough_circles(img: np.ndarray, config: dict):
    """
    Adjust the configuration parameters of cv.HoughCircles() function
    by triggers
    """
    pass


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


def find_targets(img: np.ndarray, cands: np.ndarray):
    """
    return targs = [(x, y, r, H, w), ...]

    h (Hue): Hue represents the color type and is one of the components of the
    HSV color model. The value of Hue typically ranges from 0 to 360 degrees
    and indicates the dominant color (e.g., red, green, blue, etc.).

    w (width): Width in this context describes the spread or distribution
    of Hue values after fitting a Gaussian distribution to the histogram of
    the Hue channel. This can be, for example, the standard deviation of the
    Gaussian curve that was fitted to the histogram.
    """

    # Create an targs: dict to write a list of
    # x, y, r, H, w to it for each candidate
    targs = {}

    # Clone img
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # Creating mask.
    # The size of the mask is taken from the with and height parameters
    # of the image
    mask = np.zeros(hsv_img.shape, np.uint8)

    # Around ndarray object cands for making circles masks
    # Since cv.circle accepts only an int object
    cands = np.uint16(np.around(cands))

    # Making all circles masks
    for (x, y, r) in cands[0, :]:
        cv.circle(mask, (x, y), r, (255, 255, 255), -1)

    # Bitwise hsv_img and mask
    hsv_mask_img = cv.bitwise_and(hsv_img, mask)

    # A cycle to itarete the histogram for each candidate
    # Example:
    #     candidate_1: (x, y, r, i=0)
    #     candidate_2: (x, y, r, i=1)
    #     ...
    for i, (x, y, r) in enumerate(cands[0, :]):
        # debug
        print(i, x, y, r)

        # Cropping the candidate
        hsv_cand = hsv_mask_img[y-r:y+r, x-r:x+r]

        # H channel output from HSV
        h = hsv_cand[:, :, 0]

        # Make histogram from channel Hue
        hist_h = cv.calcHist([h], [0], None, [180], [0, 179])

        x_stuff = np.arange(180)
        y_stuff = hist_h.flatten()

        # Filter x y hist data: delete point 0
        x_data = x_stuff[(x_stuff > 0)]
        y_data = y_stuff[(x_stuff > 0)]

        # Coordinate (x, y) for Alpha from gaussian function
        y_max = max(y_data)
        x_max = x_data[(y_data == y_max)][0]

        # Histogram fitting using the Gaussian function
        # popt, pcov = curve_fit(gauss_f, x_data, y_data,
        #                        p0=[y_max, x_max, math.sqrt(180)])

        # Import optimaze parameters from the object popt
        # A_opt, mu_opt, sig_opt = popt

        #
        # x_model = np.linspace(min(x_data), max(x_data), 1000)
        # y_model = gauss_f(x_model, A_opt, mu_opt, sig_opt)

        # debug
        plt.scatter(x_data, y_data)
        # plt.plot(x_model, y_model)
        plt.show()
        cv.imshow(f"hsv_cands {i+1}", hsv_cand)
        cv.waitKey()
        print(f"xy_max: {x_max, y_max}")

    # debug
    cv.imshow("mask", mask)
    cv.waitKey()
    cv.imshow("hsv_img", hsv_img)
    cv.waitKey()
    cv.imshow("hsv_mask_img", hsv_mask_img)
    cv.waitKey()


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
<<<<<<< HEAD

    cands = find_candidates(img, config["find_candidates"])
    show_candidates(img, cands)
=======
    config_data = read_config()
    #
    cands = find_candidates(img, config_data["find_candidates"])
    # show_candidates(img, cands)
>>>>>>> b3dbfba (Update detector.py for find_candidates())

    find_targets(img, cands)
