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
#############################################################################

import copy
import json
import logging

from app.config.constats import CONFIG_PATH

DEFAULT_CONF = {
    "Detector": "YOLO",
    "YOLO": {
        "model": "yolo11n-seg.pt",
        "classId": 32,
        "minConfidence": 0.1,
    },
    "GaussianBlur": {"ksize": 5, "sigmaX": 0},
    "Canny": {"threshold1": 125, "threshold2": 96},
    "Dilate": {"kernel": 8, "iterations": 3},
    "HoughCircles": {
        "dp": 1,
        "minDist": 600,
        "param1": 30,
        "param2": 17,
        "minRadius": 50,
        "maxRadius": 200,
    },
    "FindContours": {"points": 30, "minRelScale": 0.75, "maxRelScale": 1.25},
    "ShowTargets": {"points": 20},
}

logger = logging.getLogger(__name__)


class Config(object):
    def __init__(self):
        try:
            with open(CONFIG_PATH, "r") as f:
                self.__conf = json.load(f)
        except FileNotFoundError:
            logger.error("Config file not found")
            self.__conf = copy.deepcopy(DEFAULT_CONF)

    def reset(self):
        logger.info("Resetting config")
        self.__conf = copy.deepcopy(DEFAULT_CONF)

    def save(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.__conf, f, ensure_ascii=False, indent=2)

    @property
    def values(self):
        return copy.deepcopy(self.__conf)

    @property
    def k_size(self):
        return {"value": self.__conf["GaussianBlur"]["ksize"], "min": 1, "max": 20}

    @k_size.setter
    def k_size(self, value):
        self.__conf["GaussianBlur"]["ksize"] = value

    @property
    def sigma_x(self):
        return {"value": self.__conf["GaussianBlur"]["sigmaX"], "min": 0, "max": 20}

    @sigma_x.setter
    def sigma_x(self, value):
        self.__conf["GaussianBlur"]["sigmaX"] = value

    @property
    def threshold_1(self):
        return {"value": self.__conf["Canny"]["threshold1"], "min": 0, "max": 255}

    @threshold_1.setter
    def threshold_1(self, value):
        self.__conf["Canny"]["threshold1"] = value

    @property
    def threshold_2(self):
        return {"value": self.__conf["Canny"]["threshold2"], "min": 0, "max": 255}

    @threshold_2.setter
    def threshold_2(self, value):
        self.__conf["Canny"]["threshold2"] = value

    @property
    def kernel(self):
        return {"value": self.__conf["Dilate"]["kernel"], "min": 1, "max": 20}

    @kernel.setter
    def kernel(self, value):
        self.__conf["Dilate"]["kernel"] = value

    @property
    def iterations(self):
        return {"value": self.__conf["Dilate"]["iterations"], "min": 1, "max": 50}

    @iterations.setter
    def iterations(self, value):
        self.__conf["Dilate"]["iterations"] = value

    @property
    def dp(self):
        return {"value": self.__conf["HoughCircles"]["dp"], "min": 1, "max": 10}

    @dp.setter
    def dp(self, value):
        self.__conf["HoughCircles"]["dp"] = value

    @property
    def min_dist(self):
        return {"value": self.__conf["HoughCircles"]["minDist"], "min": 10, "max": 1000}

    @min_dist.setter
    def min_dist(self, value):
        self.__conf["HoughCircles"]["minDist"] = value

    @property
    def param_1(self):
        return {"value": self.__conf["HoughCircles"]["param1"], "min": 0, "max": 255}

    @param_1.setter
    def param_1(self, value):
        self.__conf["HoughCircles"]["param1"] = value

    @property
    def param_2(self):
        return {"value": self.__conf["HoughCircles"]["param2"], "min": 1, "max": 100}

    @param_2.setter
    def param_2(self, value):
        self.__conf["HoughCircles"]["param2"] = value

    @property
    def min_radius(self):
        return {
            "value": self.__conf["HoughCircles"]["minRadius"],
            "min": 0,
            "max": 1000,
        }

    @min_radius.setter
    def min_radius(self, value):
        self.__conf["HoughCircles"]["minRadius"] = value

    @property
    def max_radius(self):
        return {
            "value": self.__conf["HoughCircles"]["maxRadius"],
            "min": 0,
            "max": 1000,
        }

    @max_radius.setter
    def max_radius(self, value):
        self.__conf["HoughCircles"]["maxRadius"] = value


config = Config()

__all__ = ["config"]
