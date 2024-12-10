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

import numpy as np
from PyQt6.QtWidgets import QLabel, QPushButton

from app.windows.camera_selector import CameraSelector
from app.components.input_number import InputNumber
from app.components.video_widget import VideoWidget
from app.config.constats import CAMERA_NOT_SELECTED
from app.modules.detectors.camera_detector import CameraDetector
from app.lib.calc import is_point_in_circle
from app.lib.drawing import draw_contour, draw_center, draw_text, draw_lines
from app.lib.formaters import elide_text, np_to_pixmap
from app.lib.ui import handle_error

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.windows.main import CallABall


class CameraModule:
    def __init__(self, main_window: "CallABall"):
        self.base_point = None
        self.current_frame = None
        self.selected_ball = None
        self.balls = []
        self.camera_index = None
        self.thread_camera = None
        self._main_window = main_window

        self.btn_toggle_camera = self._main_window.findChild(
            QPushButton, "btn_toggle_camera"
        )
        self.btn_toggle_camera.clicked.connect(self.toggle_camera)

        self.btn_select_camera = self._main_window.findChild(
            QPushButton, "btn_select_camera"
        )
        self.btn_select_camera.clicked.connect(self.select_camera)
        self.label_camera_name = self._main_window.findChild(
            QLabel, "label_camera_name"
        )

        self.display_camera = self._main_window.findChild(VideoWidget, "display_camera")
        self.display_camera.clicked.connect(self.select_ball)

        self._main_window.select_calibration_result.file_selected.connect(
            self.check_field
        )
        self._main_window.input_diameter.valueChanged.connect(self.check_field)
        self._main_window.radio_media.buttonClicked.connect(self.check_field)

        self.btn_apply_coords = self._main_window.findChild(
            QPushButton, "btn_apply_coords_webcam"
        )
        self.btn_apply_coords.clicked.connect(self.apply_coords)

        self.input_camera_width = self._main_window.findChild(
            InputNumber, "input_camera_width"
        )
        self.input_camera_height = self._main_window.findChild(
            InputNumber, "input_camera_height"
        )
        self.camera_resolution_enabled(False)

    @property
    def diameter(self):
        return self._main_window.diameter

    @property
    def config_path(self):
        return self._main_window.select_calibration_result.file_path

    @property
    def is_camera_select(self):
        return self._main_window.radio_stream.isChecked()

    def select_camera(self):
        dialog = CameraSelector()
        if dialog.exec():
            if dialog.selected_camera:
                self.camera_index = dialog.camera_index
                elide_text(self.label_camera_name, dialog.selected_camera.description())
                self.camera_resolution_enabled(True)
            else:
                self.camera_index = None
                self.label_camera_name.setText(CAMERA_NOT_SELECTED)
                self.camera_resolution_enabled(False)
            self.check_field()

    def camera_processing(self):
        logger.info("camera_processing")
        self.stop_thread()
        self.start_thread()

    def stop_thread(self):
        logger.debug("thread_video delete")
        if self.thread_camera:
            self.thread_camera.requestInterruption()
            self.thread_camera.wait()
        self.thread_camera = None
        self.camera_resolution_enabled(True)

    def start_thread(self):
        logger.info("start_thread")
        if self.diameter and self.config_path and self.camera_index is not None:
            self.camera_resolution_enabled(False)
            self.btn_apply_coords_set_enabled(False)

            self.thread_camera = CameraDetector()
            self.thread_camera.frame_ready.connect(self.update_video)
            self.thread_camera.camera_resolution.connect(self.set_camera_resolution)
            self.thread_camera.error_signal.connect(handle_error)
            height = self.input_camera_height.value()
            width = self.input_camera_width.value()
            self.thread_camera.set_config(
                self.diameter, self.config_path, self.camera_index, width, height
            )
            self.thread_camera.start()

    def stop(self):
        logger.debug("camera stop")
        self.stop_thread()

    def update_video(self, image: np.array, data: list):
        self.balls = data
        self.current_frame = image
        self.__draw()

    def toggle_camera(self):
        logger.info("toggle camera")
        if self.thread_camera:
            self.stop_thread()
        else:
            self.start_thread()

    def check_field(self):
        logger.info("check_field")
        if (
            self.is_camera_select
            and self.diameter > 0
            and self.config_path
            and self.camera_index is not None
        ):
            self.camera_processing()
        else:
            self.stop()

    def select_ball(self, point: (int, int)):
        logger.info(f"select_ball {point}")
        logger.info(f"self.balls {self.balls}")
        if self.thread_camera:
            return
        selected_ball = next(
            (ball for ball in self.balls if is_point_in_circle(point, ball)), None
        )
        logger.debug(f"selected_ball: {selected_ball}")
        self.selected_ball = selected_ball
        self.btn_apply_coords_set_enabled(bool(selected_ball))
        self.__draw()

    def btn_apply_coords_set_enabled(self, enabled):
        logger.info("btn_apply_coords_set_enabled")
        self.btn_apply_coords.setEnabled(enabled)
        if not enabled:
            self.selected_ball = None

    def apply_coords(self):
        logger.info("apply_coords")
        if self.selected_ball:
            self.base_point = self.selected_ball
            self.__draw()

    def camera_resolution_enabled(self, enabled_raw: bool):
        enabled = self.camera_index is not None and enabled_raw
        self.input_camera_width.setEnabled(enabled)
        self.input_camera_height.setEnabled(enabled)

    def set_camera_resolution(self, width: int, height: int):
        self.input_camera_width.setValue(width)
        self.input_camera_height.setValue(height)

    def __draw(self):
        frame = self.current_frame.copy()
        draw_contour(frame, self.balls, self.selected_ball)
        draw_center(frame, self.balls)
        draw_text(frame, self.balls, self.base_point)
        if self.base_point:
            draw_center(frame, [self.base_point], color=(0, 255, 0))
            draw_lines(frame, self.base_point, self.balls)
        pixmap = np_to_pixmap(frame)
        self.display_camera.setPixmap(pixmap)
