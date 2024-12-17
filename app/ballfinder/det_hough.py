#!/usr/bin/env python3

# -*- coding: utf-8 -*-
#############################################################################
## Call-A-Ball: an open-source demonstrator of 3D object localization
## based on camera images and the geometric camera calibration,
## completed with the help of the Radiant Metrics cloud service.
##
## Copyright (C) 2024 HS High Stake GmbH
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.
##
## Contact: call-a-ball@high-stake.de
##
## Description: Ball detector based on Hough transform.
#############################################################################

import cv2
import numpy as np

##---------------------------------------------------------------------------
# Find circles in a binary contour map using Hough transform.

# img_c: binary contour map, array [H x W]
# return: list of candidates
#   each candidate: array [3], (x, y, r)


def detect_hough(img_c, cfg):
    dsz = cfg["Dilate"]["kernel"]
    nit = cfg["Dilate"]["iterations"]
    dp = cfg["HoughCircles"]["dp"]
    md = cfg["HoughCircles"]["minDist"]
    p1 = cfg["HoughCircles"]["param1"]
    p2 = cfg["HoughCircles"]["param2"]
    minr = cfg["HoughCircles"]["minRadius"]
    maxr = cfg["HoughCircles"]["maxRadius"]
    img_d = cv2.dilate(img_c, kernel=np.ones((dsz, dsz)), iterations=nit)
    img_q = cv2.bitwise_not(img_d)

    # Find circular contours with the Hough transform.
    res = cv2.HoughCircles(
        img_q,
        method=cv2.HOUGH_GRADIENT,
        dp=dp,
        minDist=md,
        param1=p1,
        param2=p2,
        minRadius=minr,
        maxRadius=maxr,
    )

    # Transform detections into the proper format.
    if res is None:
        return []
    cands = [np.array(cand) for cand in res[0, :]]
    return cands


##-----------------------------------------------------------------------------
