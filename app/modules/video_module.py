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

from typing import TYPE_CHECKING
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QPushButton,
    QProgressBar,
    QWidget,
)

from app.components.select_file import SelectFile
from app.modules.detectors.image_detector import ImageDetector
from app.modules.detectors.video_detector import VideoDetector
from app.modules.video_player_module import VideoPlayerModule
from app.lib.calc import is_point_in_circle
from app.lib.ui import handle_error

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if TYPE_CHECKING:
    from app.windows.main import CallABall


class VideoModule:
    def __init__(self, main_window: "CallABall"):
        self.thread_img = None
        self.thread_video = None
        self._main_window = main_window

        self.select_video = self._main_window.findChild(SelectFile, "select_video")

        self.btn_process_video = self._main_window.findChild(
            QPushButton, "btn_process_video"
        )
        self.btn_process_video.clicked.connect(self.video_processing)

        self.btn_detect_ball = self._main_window.findChild(
            QPushButton, "btn_detect_ball"
        )
        self.btn_detect_ball.clicked.connect(self.detect_ball)

        self.btn_apply_coords = self._main_window.findChild(
            QPushButton, "btn_apply_coords"
        )
        self.btn_apply_coords.clicked.connect(self.apply_coords)

        self.box_controls = self._main_window.findChild(QWidget, "box_controls")

        self.progress_bar = self._main_window.findChild(
            QProgressBar, "progress_bar_video"
        )
        self.btn_stop_processing = self._main_window.findChild(
            QPushButton, "btn_stop_processing"
        )
        self.btn_stop_processing.clicked.connect(self.stop)

        self.widget_progress_video = self._main_window.findChild(
            QWidget, "widget_progress_video"
        )
        self.widget_progress_video.hide()

        self.select_video.file_selected.connect(self.check_field)
        self._main_window.select_calibration_result.file_selected.connect(
            self.check_field
        )
        self._main_window.input_diameter.valueChanged.connect(self.check_field)
        self._main_window.radio_media.buttonClicked.connect(self.check_field)

        self.video_player = VideoPlayerModule(self._main_window)
        self.video_player.play_signal.connect(self.play_handler)
        self.video_player.set_position_signal.connect(self.play_handler)
        self.video_player.video_widget.clicked.connect(self.select_ball)

    @property
    def video_path(self):
        return self.select_video.file_path

    @property
    def diameter(self):
        return self._main_window.diameter

    @property
    def config_path(self):
        return self._main_window.select_calibration_result.file_path

    @property
    def is_video_select(self):
        return self._main_window.radio_video.isChecked()

    def video_processing(self):
        logger.info("video_processing")
        self.update_progress(0)
        self.widget_progress_video.show()
        self.set_enabled_controls(False)
        self.video_player.pause()

        self.stop_thread()
        self.thread_video = VideoDetector()
        self.thread_video.video_progress.connect(self.update_progress)
        self.thread_video.data_ready.connect(self.update_video_data)
        self.thread_video.error_signal.connect(handle_error)
        self.thread_video.set_config(self.diameter, self.config_path, self.video_path)
        self.thread_video.start()

    def stop_thread(self):
        logger.debug("thread_video delete")
        if self.thread_video:
            self.thread_video.requestInterruption()
            self.thread_video.wait()
        self.thread_video = None

    def stop(self):
        logger.debug("video processing stop")
        self.stop_thread()
        self.set_enabled_controls(True)
        self.widget_progress_video.hide()

    def set_enabled_controls(self, enabled: bool):
        self.box_controls.setEnabled(enabled)
        self.video_player.set_enabled_controls(enabled)
        self.btn_process_video.setEnabled(enabled)
        self.btn_detect_ball.setEnabled(enabled)

    def update_progress(self, progress: float):
        self.progress_bar.setValue(int(progress * 100))

    def check_field(self):
        logger.info("check_field")
        if (
            self.is_video_select
            and self.diameter > 0
            and self.config_path
            and self.video_path
        ):
            logger.debug("check_field: ready")
            self.btn_process_video.setEnabled(True)
            self.btn_detect_ball.setEnabled(True)
        else:
            logger.debug("check_field: not ready")
            self.stop()
            self.btn_process_video.setEnabled(False)
            self.btn_detect_ball.setEnabled(False)

    def detect_ball(self):
        logger.info("detect_ball")
        if (
            self.video_player.current_frame is not None
            and self.thread_img is None
            and not self.video_player.is_playing
        ):
            self.btn_detect_ball.setEnabled(False)
            self.video_player.set_enabled_controls(False)
            image = self.video_player.current_frame
            self.thread_img = ImageDetector()
            self.thread_img.set_config(self.diameter, self.config_path, image)
            self.thread_img.image_data.connect(self.update_img_data)
            self.thread_img.error_signal.connect(self.update_frame_error)
            self.thread_img.start()

    def update_frame_error(self):
        logger.info("update_frame_error")
        self.btn_detect_ball.setEnabled(True)
        self.video_player.set_enabled_controls(True)
        self.thread_img = None

    def select_ball(self, point: (int, int)):
        logger.info(f"select_ball {point}")
        balls = self.video_player.get_current_balls()
        selected_ball = next(
            (ball for ball in balls if is_point_in_circle(point, ball)), None
        )
        logger.debug(f"selected_ball: {selected_ball}")
        self.video_player.selected_ball = selected_ball
        self.btn_apply_coords_set_enabled(bool(selected_ball))
        self.video_player.update_current_frame()

    def play_handler(self):
        self.btn_apply_coords_set_enabled(False)

    def update_video_data(self, balls: dict):
        logger.info("update_video_data")
        self.video_player.set_balls(balls)
        self.stop()
        QTimer.singleShot(0, self.video_player.update_current_frame)

    def update_img_data(self, balls: list):
        logger.info("update_img_data")
        self.video_player.set_current_balls(balls)
        self.btn_detect_ball.setEnabled(True)
        self.video_player.set_enabled_controls(True)
        self.thread_img = None
        self.video_player.update_current_frame()

    def apply_coords(self):
        logger.info("apply_coords")
        if self.video_player.selected_ball:
            self.video_player.base_point = self.video_player.selected_ball
            self.video_player.update_current_frame()

    def btn_apply_coords_set_enabled(self, enabled):
        logger.info("btn_apply_coords_set_enabled")
        self.btn_apply_coords.setEnabled(enabled)
        if not enabled:
            self.video_player.selected_ball = None
