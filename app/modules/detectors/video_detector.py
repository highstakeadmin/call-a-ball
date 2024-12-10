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
from PyQt6.QtCore import QThread, pyqtSignal
from moviepy import VideoFileClip

from app.ballfinder.ballfinder import BallFinder
from app.config.config import config
from app.lib.config import read_camera_config

logger = logging.getLogger(__name__)


class VideoDetector(QThread):
    data_ready = pyqtSignal(dict)
    video_progress = pyqtSignal(float)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._config_path = None
        self._video_path = None
        self._diameter = None

    def set_config(self, diameter, config_path, video_path):
        self._diameter = diameter
        self._config_path = config_path
        self._video_path = video_path

    def detect_video(self):
        video = cv2.VideoCapture(self._video_path)
        clip = VideoFileClip(self._video_path)
        if video is None:
            raise Exception("Error loading the video.")

        width, height = clip.size
        camera = read_camera_config(self._config_path, height, width)

        frame_count = clip.reader.n_frames - 1

        cfg = config.values

        logger.info("Start video detector")
        i = 0
        data = {}
        ball_finder = BallFinder(cfg)
        while not self.isInterruptionRequested():
            ret, frame = video.read()
            if not ret:
                break
            i += 1

            (res, err) = ball_finder.find_balls(frame, self._diameter / 2, camera)

            if err:
                logger.debug(f"findTargets error: {err}")
                logger.info(f"skip {i} frame")
            else:
                data[i] = res
            logger.info(f"Processed {i}/{frame_count} frame")
            self.video_progress.emit(i / frame_count)
        video.release()
        return data

    def run(self):
        try:
            balls = self.detect_video()
            if not self.isInterruptionRequested():
                self.data_ready.emit(balls)
        except Exception as err:
            logger.info("Video Processing Error")
            self.error_signal.emit(str(err))
