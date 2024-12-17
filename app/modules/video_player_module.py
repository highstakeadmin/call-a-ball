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
from collections import defaultdict
from typing import Any

import numpy as np
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import (
    QLabel,
    QSlider,
    QWidget,
    QMainWindow,
)

from app.components.btn_play_pause import BtnPlayPause
from app.components.input_number import InputNumber
from app.components.select_file import SelectFile
from app.components.video_widget import VideoWidget
from app.config.constats import PlaybackState
from app.modules.media_player import MediaPlayer
from app.lib.drawing import draw_contour, draw_center, draw_text, draw_lines
from app.lib.formaters import np_to_pixmap

logger = logging.getLogger(__name__)


class VideoPlayerModule(QObject):
    play_signal = pyqtSignal()
    set_position_signal = pyqtSignal()
    pause_signal = pyqtSignal()

    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.base_point = None
        self.balls = defaultdict(lambda: [])
        self.selected_ball = None
        self._main_window = main_window

        self.select_video = self._main_window.findChild(SelectFile, "select_video")
        self.select_video.file_selected.connect(self.set_video)

        self.video_widget = self._main_window.findChild(VideoWidget, "display_video")

        self.player = MediaPlayer()
        self.player.video_frame_changed.connect(self.__frame_changed_handler)
        self.player.state_changed.connect(self.__video_state_changed_handler)

        self.widget_player_control = self._main_window.findChild(
            QWidget, "widget_player_control"
        )

        self.slider_video = self._main_window.findChild(QSlider, "slider_video")
        self.slider_video.valueChanged.connect(self.__set_position)

        self.input_frame_number = self._main_window.findChild(
            InputNumber, "input_frame_number"
        )
        self.input_frame_number.valueSubmitted.connect(self.__set_position)
        self.label_frame_total = self._main_window.findChild(
            QLabel, "label_frame_total"
        )

        self.btn_play_pause = self._main_window.findChild(
            BtnPlayPause, "btn_play_pause"
        )
        self.btn_play_pause.play.connect(self.player.play)
        self.btn_play_pause.pause.connect(self.player.pause)

    def __set_position(self, frame_number: int):
        self.player.pause()
        self.player.set_position(frame_number)
        self.__update_frame_number(frame_number)
        self.set_position_signal.emit()

    def __video_state_changed_handler(self, status: str):
        logger.info(f"The player's status has changed: {status}")
        if status == PlaybackState.stop:
            self.btn_play_pause.set_pause()
            self.pause_signal.emit()
        if status == PlaybackState.pause:
            self.btn_play_pause.set_pause()
            self.pause_signal.emit()
        if status == PlaybackState.play:
            self.btn_play_pause.set_play()
            self.play_signal.emit()

    def __media_status_changed_handler(self, status):
        logger.debug("__media_status_changed_handler")
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.__set_position(0)

    def __frame_changed_handler(self, frame: np.ndarray, frame_number: int):
        logger.debug(f"__frame_changed_handler: {frame_number}")
        balls = self.balls[frame_number]
        image = frame.copy()
        if len(balls) > 0:
            draw_contour(image, balls, self.selected_ball)
            draw_center(image, balls)
            draw_text(image, balls, self.base_point)
            if self.base_point:
                draw_center(image, [self.base_point], color=(0, 255, 0))
                draw_lines(image, self.base_point, balls)
        pixmap = np_to_pixmap(image)
        self.video_widget.setPixmap(pixmap)
        self.__update_frame_number(frame_number)

    def __update_frame_number(self, frame_number: int):
        logger.debug(f"update_frame_number {frame_number}")
        self.slider_video.blockSignals(True)
        self.slider_video.setValue(frame_number)
        self.slider_video.blockSignals(False)

        self.input_frame_number.blockSignals(True)
        self.input_frame_number.setValue(frame_number)
        self.input_frame_number.blockSignals(False)

    @property
    def is_playing(self):
        return self.player.is_playing

    @property
    def current_frame(self) -> np.ndarray:
        if self.player.current_frame is not None:
            return self.player.current_frame.copy()

    @property
    def current_frame_number(self):
        return self.player.current_frame_number

    def get_current_balls(self) -> list[Any]:
        return self.balls[self.current_frame_number]

    def set_current_balls(self, balls: list[Any]):
        self.balls[self.current_frame_number] = balls

    def set_balls(self, balls: dict):
        self.balls = defaultdict(lambda: [], balls)

    def set_video(self, video_path: str or None):
        logger.debug(f"set_video: {video_path}")

        self.base_point = None
        self.balls = defaultdict(lambda: [])
        self.selected_ball = None

        if video_path:
            self.player.set_source(video_path)
            self.widget_player_control.setEnabled(True)
        else:
            self.player.clear()
            self.widget_player_control.setEnabled(False)

        frame_count = self.player.frame_count
        self.label_frame_total.setText(f"of {frame_count}")
        self.input_frame_number.setMaximum(frame_count)
        self.slider_video.setMaximum(frame_count)

    def update_current_frame(self):
        logger.debug("update_current_frame")
        self.__frame_changed_handler(self.current_frame, self.current_frame_number)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def set_enabled_controls(self, enabled):
        self.widget_player_control.setEnabled(enabled)
