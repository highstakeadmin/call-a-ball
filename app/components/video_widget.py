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

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPixmap
from PyQt6.QtWidgets import QLabel

from app.lib.ui import update_pixmap

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class VideoWidget(QLabel):
    clicked = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None

    def mousePressEvent(self, event: QMouseEvent):
        position = event.position()
        widget_x = position.x()
        widget_y = position.y()
        logger.debug(f"raw position: x:{widget_x} y:{widget_y}")

        if self._pixmap is None:
            return

        img_size = self._pixmap.size()
        logger.debug(f"img_size: {img_size}")
        widget_size = self.size()

        if not img_size.isValid():
            return

        video_width = img_size.width()
        video_height = img_size.height()
        widget_width = widget_size.width()
        widget_height = widget_size.height()
        logger.debug(f"video_width: {video_width}x{widget_height}")
        logger.debug(f"widget_size: {widget_width}x{widget_height}")

        video_ratio = video_width / video_height
        widget_ratio = widget_width / widget_height

        if widget_ratio > video_ratio:
            scale_factor = widget_height / video_height
            offset_x = (widget_width - video_width * scale_factor) / 2
            offset_y = 0
        else:
            scale_factor = widget_width / video_width
            offset_x = 0
            offset_y = (widget_height - video_height * scale_factor) / 2

        video_x = int((widget_x - offset_x) / scale_factor)
        video_y = int((widget_y - offset_y) / scale_factor)

        if 0 <= video_x <= video_width and 0 <= video_y <= video_height:
            logger.debug(f"position: x={video_x}, y={video_y}")
            self.clicked.emit((video_x, video_y))
        else:
            logger.debug("outside click")

    def setPixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        update_pixmap(self._pixmap, super())

    def resizeEvent(self, event):
        update_pixmap(self._pixmap, super())
