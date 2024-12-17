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

import logging

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from app.ballfinder.ballfinder import BallFinder
from app.config.config import config
from app.lib.config import read_camera_config
from app.lib.drawing import draw_contour, draw_center, draw_text

logger = logging.getLogger(__name__)


class ImageDetector(QThread):
    image_ready = pyqtSignal(np.ndarray)
    image_data = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._config_path = None
        self._img = None
        self._diameter = None

    def set_config(self, diameter, config_path, img):
        self._diameter = diameter
        self._config_path = config_path
        self._img = img

    def detect_image(self, image) -> (np.ndarray, list):
        height, width, _ = image.shape
        camera = read_camera_config(self._config_path, height, width)
        if self.isInterruptionRequested():
            return None, []

        cfg = config.values
        if self.isInterruptionRequested():
            return None, []

        logger.debug(f"findTargets; diameter: {self._diameter}")
        ball_finder = BallFinder(cfg)
        (res, err) = ball_finder.find_balls(image, self._diameter / 2, camera)

        logger.debug(f"res: {res}")
        if err:
            logger.error(f"findTargets error: {err}")
            raise Exception(err)
        if self.isInterruptionRequested():
            return None, []

        draw_contour(image, res)
        draw_center(image, res)
        draw_text(image, res)
        return image, res

    def start_tread(self) -> (np.ndarray, list):
        if isinstance(self._img, str):
            image = cv2.imread(self._img)
            if image is None:
                raise Exception("Error loading the image.")
            if self.isInterruptionRequested():
                return None, []
        else:
            image = self._img

        return self.detect_image(image)

    def run(self):
        try:
            logger.debug("ImageDetector run")
            img, balls = self.start_tread()
            if img is not None:
                logger.debug("Image ready")
                self.image_ready.emit(img)
                self.image_data.emit(balls)
        except Exception as err:
            logger.error(f"ImageDetector err: {err}")
            self.error_signal.emit(str(err))
