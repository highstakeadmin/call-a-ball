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
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.config.constats import PlaybackState

logger = logging.getLogger(__name__)


class MediaPlayer(QObject):
    video_frame_changed = pyqtSignal((np.ndarray, int))
    state_changed = pyqtSignal(PlaybackState)

    def __init__(self):
        super().__init__()
        self.frame_count = None
        self.fps = None
        self.cap = None
        self.current_frame = None
        self.current_frame_number = None
        self.clear()

        self.timer = QTimer()
        self.timer.timeout.connect(self.__next_frame)

    def set_source(self, video_path: str):
        self.current_frame_number = 0
        self.cap = cv2.VideoCapture(video_path)
        clip = VideoFileClip(video_path)
        self.fps = clip.fps
        self.frame_count = clip.reader.n_frames - 1
        self.__next_frame()
        logger.debug(f"set_source; fps: {self.fps}; frame_count: {self.frame_count}")

    def clear(self):
        self.frame_count = 0
        self.fps = None
        self.cap = None
        self.current_frame = None
        self.current_frame_number = 0
        self.__update_frame(np.empty((0, 0, 3)), 0)

    def set_position(self, frame_number: int):
        logger.debug(
            f"set_position; frame_number: {frame_number}; self.frame_count: {self.frame_count}"
        )
        if 0 < frame_number <= self.frame_count:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
            ret, frame = self.cap.read()
            if ret:
                self.__update_frame(frame, frame_number)

    def play(self):
        logger.debug("play")
        if not self.timer.isActive():
            if self.current_frame_number == self.frame_count:
                self.__reset()
            self.state_changed.emit(PlaybackState.play)
            self.timer.start(int(1000 / self.fps))

    def pause(self):
        if self.timer.isActive():
            self.state_changed.emit(PlaybackState.pause)
            self.timer.stop()

    @property
    def is_playing(self):
        return self.timer.isActive()

    def __next_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.state_changed.emit(PlaybackState.stop)
            return

        self.__update_frame(frame, self.current_frame_number + 1)

    def __reset(self):
        self.current_frame_number = 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def __update_frame(self, frame: np.ndarray, frame_number: int):
        logger.debug(f"__update_frame; frame_number: {frame_number}")
        self.current_frame_number = frame_number
        self.current_frame = frame
        self.video_frame_changed.emit(frame, frame_number)
