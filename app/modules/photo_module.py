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

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
from app.components.select_file import SelectFile
from app.modules.detectors.image_detector import ImageDetector
from app.lib.formaters import np_to_pixmap
from app.lib.ui import handle_error, update_pixmap

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.windows.main import CallABall


class PhotoModule:
    def __init__(self, main_window: "CallABall"):
        logger.info("init")
        self._photo_path = None
        self._config_path = None
        self._diameter = None
        self.thread_img: ImageDetector or None = None
        self._main_window = main_window
        self.pixmap = None
        self.select_photo = self._main_window.findChild(SelectFile, "select_photo")

        self.display_photo = self._main_window.findChild(QLabel, "display_photo")

        self.select_photo.file_selected.connect(self.check_field)
        self._main_window.select_calibration_result.file_selected.connect(
            self.check_field
        )
        self._main_window.input_diameter.valueChanged.connect(self.check_field)
        self._main_window.radio_media.buttonClicked.connect(self.check_field)

    @property
    def diameter(self):
        return self._main_window.diameter

    @property
    def config_path(self):
        return self._main_window.select_calibration_result.file_path

    @property
    def is_photo_select(self):
        return self._main_window.radio_photo.isChecked()

    @property
    def photo_path(self):
        return self.select_photo.file_path

    def photo_processing(self):
        logger.info("photo_processing")
        self.stop_thread()
        self.thread_img = ImageDetector()
        self.thread_img.image_ready.connect(self.update_image)
        self.thread_img.image_ready.connect(self.stop_thread)
        self.thread_img.error_signal.connect(handle_error)

        self.pixmap = QPixmap(self.photo_path)
        self.resize()
        self.thread_img.set_config(self.diameter, self.config_path, self.photo_path)
        self.thread_img.start()

    def stop_thread(self):
        logger.debug("thread_img delete")
        if self.thread_img:
            self.thread_img.requestInterruption()
            self.thread_img.wait()
        self.thread_img = None

    def stop(self):
        logger.debug("image stop")
        self.stop_thread()

    def resize(self):
        update_pixmap(self.pixmap, self.display_photo)

    def update_image(self, image_data):
        self.pixmap = np_to_pixmap(image_data)
        self.resize()

    def check_field(self):
        logger.info("check_field")
        if (
            self.is_photo_select
            and self.diameter > 0
            and self.config_path
            and self.photo_path
            and (
                self._diameter != self.diameter
                or self._config_path != self.config_path
                or self._photo_path != self.photo_path
            )
        ):
            self._diameter = self.diameter
            self._config_path = self.config_path
            self._photo_path = self.photo_path
            self.photo_processing()
        else:
            self.stop()
