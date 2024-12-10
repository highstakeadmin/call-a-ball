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
## Description: Detector of spherical objects in images.
#############################################################################

from .det_util import *
from .det_hough import detect_hough
from .det_yolo import init_yolo, detect_yolo


class BallFinder(object):

    ##---------------------------------------------------------------------------
    # Initialize the detector of balls.

    # cfg: configuration dict

    def __init__(self, cfg):
        self.cfg = cfg
        if self.cfg["Detector"] == "YOLO":
            self.yolo = init_yolo(self.cfg["YOLO"]["model"])
            return
        if self.cfg["Detector"] == "HOUGH":
            return
        assert 0  # the detector is undefined or invalid

    ##---------------------------------------------------------------------------
    # Detect balls in an image.

    # img_bgr: color image, array [H x W x 3]
    # radius: float, a priori known ball radius
    # camera: dict of camera parameters
    # return: (res, err),
    #   res: list of detections
    #     detection: dict, main fields: {
    #       'target': (X, Y, Z, radius),
    #       '2d_center': (x, y),
    #       '2d_contour': [(x, y), ...],
    #       'candidate': (x, y, r)
    #     }
    #   err: string of error messages, empty on success

    def find_balls(self, img_bgr, radius, camera):
        res = []
        try:
            (img_c, fun_c) = canny(img_bgr, self.cfg)
            if self.cfg["Detector"] == "YOLO":
                cands_0 = detect_yolo(self.yolo, img_bgr, self.cfg)
            if self.cfg["Detector"] == "HOUGH":
                cands_0 = detect_hough(img_c, self.cfg)
            conts_0 = [find_contour(cand, fun_c, self.cfg) for cand in cands_0]
            (cands_1, conts_1) = ([], [])
            for cand, cont in zip(cands_0, conts_0):
                if not valid_contour(cont, self.cfg):
                    continue
                cands_1.append(cand)
                conts_1.append(cont)
            cones_1 = [
                find_cone(cand, cont, camera) for (cand, cont) in zip(cands_1, conts_1)
            ]
            balls_1 = [fit_ball(cone, radius) for cone in cones_1]
            balls_2 = [
                refine_ball(ball, cone, radius, self.cfg)
                for (ball, cone) in zip(balls_1, cones_1)
            ]
            ctrps_2 = [
                project_center(ball, cand, radius, camera)
                for (ball, cand) in zip(balls_2, cands_1)
            ]
            conts_2 = [
                project_contour(ball, cont, radius, camera, self.cfg)
                for (ball, cont) in zip(balls_2, conts_1)
            ]

            for cand, ball, ctrp, cont in zip(cands_1, balls_2, ctrps_2, conts_2):
                (x, y, r) = cand
                (X, Y, Z) = ball
                (a, b) = ctrp
                res.append(
                    {
                        "target": (X, Y, Z, radius),
                        "2d_center": (a, b),
                        "2d_contour": [(x, y) for (x, y) in cont],
                        "candidate": (x, y, r),
                    }
                )

        except Exception as e:
            print(e)
            return (res, str(e))
        return (res, "")


##-----------------------------------------------------------------------------
