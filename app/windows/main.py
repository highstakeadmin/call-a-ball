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

import logging
import os

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QMainWindow,
    QDoubleSpinBox,
    QStackedWidget,
    QButtonGroup,
    QAbstractButton,
    QRadioButton,
)
from PyQt6.uic import loadUi

from app.components.select_file import SelectFile
from app.config.constats import ROOT_PATH
from app.modules.camera_module import CameraModule
from app.modules.menu_bar_module import MenuBarModule
from app.modules.photo_module import PhotoModule
from app.modules.video_module import VideoModule

from app.styles.main_qss import main_qss

logger = logging.getLogger(__name__)


class CallABall(QMainWindow):
    def __init__(self):
        super(CallABall, self).__init__()
        loadUi("ui/main_window.ui", self)
        font_path = os.path.join(ROOT_PATH, "resources", "fonts", "NotoSans.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            logger.error("Error: the font could not be loaded.")
            return

        self.setStyleSheet(main_qss)

        self.menu_bar = MenuBarModule(self)

        self.show_media = self.findChild(QStackedWidget, "show_media")
        self.show_media.setCurrentIndex(0)
        self.select_media = self.findChild(QStackedWidget, "select_media")
        self.select_media.setCurrentIndex(0)

        self.radio_photo = self.findChild(QRadioButton, "radio_photo")
        self.radio_video = self.findChild(QRadioButton, "radio_video")
        self.radio_stream = self.findChild(QRadioButton, "radio_stream")
        self.radio_media = self.findChild(QButtonGroup, "radio_media")
        self.radio_media.buttonClicked.connect(self.switch_media)

        self.select_calibration_result = self.findChild(
            SelectFile, "select_calibration_result"
        )

        self.photo_section = PhotoModule(self)
        logger.info(f"self.photo_section: {self.photo_section}")
        self.video_section = VideoModule(self)
        self.camera_section = CameraModule(self)

        self.input_diameter = self.findChild(QDoubleSpinBox, "input_diameter")

    @property
    def diameter(self):
        return self.input_diameter.value()

    def resizeEvent(self, event):
        logger.info("resizeEvent")
        if self.radio_photo.isChecked():
            self.photo_section.resize()
        super().resizeEvent(event)

    def switch_media(self, btn: QAbstractButton):
        logger.debug("switch_media")
        if btn.objectName() == "radio_photo":
            self.select_media.setCurrentIndex(0)
            self.show_media.setCurrentIndex(0)
        elif btn.objectName() == "radio_video":
            self.select_media.setCurrentIndex(1)
            self.show_media.setCurrentIndex(1)
        elif btn.objectName() == "radio_stream":
            self.select_media.setCurrentIndex(2)
            self.show_media.setCurrentIndex(2)

    def disable_buttons(self):
        self.select_calibration_result.setEnabled(False)
        self.input_diameter.setEnabled(False)
        self.radio_photo.setEnabled(False)
        self.radio_video.setEnabled(False)
        self.radio_stream.setEnabled(False)

    def enable_buttons(self):
        self.select_calibration_result.setEnabled(True)
        self.input_diameter.setEnabled(True)
        self.radio_photo.setEnabled(True)
        self.radio_video.setEnabled(True)
        self.radio_stream.setEnabled(True)
