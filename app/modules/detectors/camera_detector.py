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
from queue import Queue

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QRunnable, QThreadPool

from app.ballfinder.ballfinder import BallFinder
from app.config.config import config
from app.lib.config import read_camera_config

logger = logging.getLogger(__name__)


class Worker(QRunnable):
    def __init__(self, function, *args):
        super().__init__()
        self.function = function
        self.args = args

    def run(self):
        self.function(*self.args)


class CameraDetector(QThread):
    frame_ready = pyqtSignal((np.ndarray, list))
    camera_resolution = pyqtSignal((int, int))
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._config_path = None
        self._camera_index = None
        self._diameter = None

        self.fps = 20
        self.show_video = False
        self.delay_buffer = Queue()
        self.ready_frames = Queue()
        self.detection = None

        self.width = 10000
        self.height = 10000

    def set_config(self, diameter, config_path, camera_index, width: int, height: int):
        self._diameter = diameter
        self._config_path = config_path
        self._camera_index = camera_index
        self.width = width
        self.height = height

    def init_camera(self):
        logger.info("init_camera")
        capture = cv2.VideoCapture(self._camera_index)
        capture.set(cv2.CAP_PROP_FPS, self.fps)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Camera size: {int(width)} x {int(height)}")
        return capture, width, height

    def read_config(self, width: int, height: int):
        camera = read_camera_config(self._config_path, height, width)
        return camera, config.values

    def detect(self, camera, cfg):
        count = 0
        ball_finder = BallFinder(cfg)
        while not self.isInterruptionRequested():
            if self.delay_buffer.empty():
                continue
            self.update_frame()
            frame = self.delay_buffer.get()
            (res, err) = ball_finder.find_balls(frame, self._diameter / 2, camera)

            if err:
                logger.debug(f"findTargets error: {err}")
                logger.info(f"skip frame")
            else:
                self.detection = res

            if count > 4:
                self.show_video = True
            else:
                count += 1
            self.ready_frames.put((frame, self.detection))
        self.show_video = False

    def update_frame(self):
        if self.detection is None:
            return
        frame_count = self.delay_buffer.qsize()
        for i in range(frame_count):
            frame = self.delay_buffer.get()
            self.ready_frames.put((frame, self.detection))

    def processing_frame(self, capture):
        logger.info("processing_frame")
        while not self.isInterruptionRequested():
            ret, frame = capture.read()

            if ret:
                self.delay_buffer.put(frame)
                if self.show_video:
                    frame, data = self.ready_frames.get()
                    self.frame_ready.emit(frame, data)

        capture.release()

    def run(self):
        try:
            thread_pool = QThreadPool()
            capture, width, height = self.init_camera()
            self.camera_resolution.emit(width, height)
            camera, cfg = self.read_config(width, height)
            thread_pool.start(Worker(self.processing_frame, capture))
            thread_pool.start(Worker(self.detect, camera, cfg))
        except Exception as err:
            self.error_signal.emit(str(err))
