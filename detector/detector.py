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
import json
import math
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

    # Expansion of the faces after Canny processing
    dilate_data = config["dilate"]
    kernel = np.ones((  # kernel radius for dilate
        dilate_data["kernel"], dilate_data["kernel"]
    ))
    dil = cv.dilate(canny, kernel=kernel, iterations=dilate_data["iterations"])
    dil = cv.bitwise_not(dil)  # invert color

    # Use Hough transform to find circular contours.
    hough_data = config["hough_circles"]
    circles = cv.HoughCircles(
        dil,
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
    for (x, y, r) in cands[0, :]:
        cv.circle(clone_img, (x, y), r, (0, 255, 0), 3)
        cv.circle(clone_img, (x, y), 3, (0, 255, 255), 5)

    # Show image with candidates
    cv.namedWindow("detected_circles", cv.WINDOW_NORMAL)
    cv.imshow("detected_circles", clone_img)
    cv.waitKey()
    cv.destroyAllWindows()


def filter_target(A_opt, mu_opt, sig_opt,
                  A_err, mu_err, sig_err,
                  conf: dict):
    """A function for filtering candidates by parameters from config.json

    After passing a number of conditions, it outputs either True
    or False for one candidate
    """
    if sig_opt < 0 or A_err > conf["A_err"] or mu_err > conf["mu_err"]:
        return True
    return False


def find_targets(img: np.ndarray, cands: np.ndarray, config: dict):
    """
    Return targs as a list of tuples containing
    the following elements for each candidate:

    targs = (x, y, r, A, mu, sig, A_err, mu_err, sig_err)

    Where:
    - (x, y): Coordinates of the candidate circle center.
    - r: Radius of the candidate circle.
    - A: Amplitude parameter of the fitted Gaussian function,
    representing the peak value.
    - mu: Mean parameter of the fitted Gaussian function,
    representing the center or peak position.
    - sig: Standard deviation parameter of the fitted Gaussian function,
    representing the spread or width.
    - A_err: Standard error of the amplitude parameter A,
    indicating the uncertainty in its estimation.
    - mu_err: Standard error of the mean parameter mu,
    indicating the uncertainty in its estimation.
    - sig_err: Standard error of the standard deviation parameter sig,
    indicating the uncertainty in its estimation.

    These parameters provide a comprehensive description of
    each candidate's characteristics after fitting
    a Gaussian function to the histogram data derived
    from the candidate region in the HSV image.
    """

    # Create an targs: list of
    # x, y, r, A, mu, sig, A_err, mu_err, sig_err to it for each candidate
    targs = []

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
        popt, pcov = curve_fit(gauss_f, x_data, y_data,
                               p0=[y_max, x_max, math.sqrt(180)])

        # Import optimaze parameters from the object popt
        A_opt, mu_opt, sig_opt = popt
        # Calculate standard errors of the parameters
        A_err, mu_err, sig_err = np.sqrt(np.diag(pcov))

        # Filter target
        filter_config = config["filter_target"]
        if filter_target(
            A_opt, mu_opt, sig_opt,
            A_err, mu_err, sig_err,
            conf=filter_config
        ):
            continue

        # Make at array
        targs.append((x, y, r, A_opt, mu_opt, sig_opt, A_err, mu_err, sig_err))

    return targs


def show_targets(img: np.ndarray, targs):
    """A function displaying a table from:

    [HSV_image, histogram]

    Show:
    HSV_image - the image in the HSV channel
    histogram - a histogram combining the number of pixels
    per channel H (blue points) and a fitted Gaussian function (blue line)

    Input:
    targs = (x, y, r, A, mu, sig, A_err, mu_err, sig_err)
    img - original image (BGR)
    """
    # Clone img
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    # Creating mask.
    # The size of the mask is taken from the with and height parameters
    # of the image
    mask = np.zeros(hsv_img.shape, np.uint8)

    # Make a cicle
    for i, (x, y, r, A_opt, mu_opt, sig_opt, A_err, mu_err, sig_err) \
            in enumerate(targs):

        # Print all parameters with candidates number for debug
        print(f"Index: {i}, x: {x}, y: {y}, r: {r}, "
              f"A_opt: {A_opt}, mu_opt: {mu_opt}, sig_opt: {sig_opt}, "
              f"A_err: {A_err}, mu_err: {mu_err}, sig_err: {sig_err}")

        # Create mask for HSV candidate
        cv.circle(mask, (x, y), r, (255, 255, 255), -1)
        hsv_mask_img = cv.bitwise_and(hsv_img, mask)
        hsv_cand = hsv_mask_img[y-r:y+r, x-r:x+r]

        # Create mask for RGB candidate
        rgb_mask_img = cv.bitwise_and(rgb_img, mask)
        rgb_cand = rgb_mask_img[y-r:y+r, x-r:x+r]

        # H channel output from HSV
        h = hsv_cand[:, :, 0]

        # Make histogram from channel Hue
        hist_h = cv.calcHist([h], [0], None, [180], [0, 179])

        x_stuff = np.arange(180)
        y_stuff = hist_h.flatten()

        # Filter x y hist data: delete point 0
        x_data = x_stuff[(x_stuff > 0)]
        y_data = y_stuff[(x_stuff > 0)]

        x_model = np.linspace(min(x_data), max(x_data), 1000)
        y_model = gauss_f(x_model, A_opt, mu_opt, sig_opt)

        # Make table [hsv_cands: image, histogram]
        _, axs = plt.subplots(1, 2)

        # Show HSV image
        axs[0].imshow(rgb_cand)
        axs[0].set_title("HSV_Image")

        # Show histogram
        axs[1].scatter(x_data, y_data)
        axs[1].plot(x_model, y_model, "red")
        axs[1].set_title("Hue_Histogram")
        axs[1].set_xlabel("hue_color")
        axs[1].set_ylabel("#pixels")
        plt.show()


def find_contour(img, targ):
    pass


def show_contour(pmap):
    pass


# Entry point for quick tests
if __name__ == "__main__":
    config = read_json("detector/config.json")
    img = cv.imread("detector/images/desk1.jpeg")

    cands = find_candidates(img, config["find_candidates"])
    show_candidates(img, cands)

    targets = find_targets(img, cands, config["find_targets"])

    show_targets(img, targets)
