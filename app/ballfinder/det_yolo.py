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
## Description: Ball detector based on a pre-trained YOLO model.
#############################################################################

import numpy as np


def init_yolo(model_name):
    from ultralytics import YOLO

    return YOLO(model_name)


##-----------------------------------------------------------------------------
# Find spheres in the image using a pre-trained YOLO model.

# img_bgr: color image, array [H x W x 3]
# return: list of candidates
#   each candidate: array [3], (x, y, r)


def detect_yolo(yolo, img_bgr, cfg):
    class_id = cfg["YOLO"]["classId"]
    min_conf = cfg["YOLO"]["minConfidence"]
    res = yolo(img_bgr, classes=[class_id], conf=min_conf, verbose=False)
    if len(res) < 1:
        return []
    cands = []
    boxes = np.array(res[0].boxes.xyxy.cpu())
    for i in range(boxes.shape[0]):
        (xa, ya, xb, yb) = boxes[i, :]
        (x, y) = (0.5 * (xa + xb), 0.5 * (ya + yb))
        r = 0.25 * ((xb - xa) + (yb - ya))
        cands.append(np.array([x, y, r]))
    return cands


##-----------------------------------------------------------------------------
