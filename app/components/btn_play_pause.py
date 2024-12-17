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

from PyQt6.QtWidgets import QStyle, QPushButton
from PyQt6.QtCore import pyqtSignal

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BtnPlayPause(QPushButton):
    play = pyqtSignal()
    pause = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        style = self.style()
        self.play_icon = style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.pause_icon = style.standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        self._is_playing = False
        self.setIcon(self.play_icon)
        self.clicked.connect(self.click_handler)

    def click_handler(self):
        logger.debug("click_handler")
        if self._is_playing:
            self._is_playing = False
            self.setIcon(self.play_icon)
            self.pause.emit()
        else:
            self._is_playing = True
            self.setIcon(self.pause_icon)
            self.play.emit()

    def set_play(self):
        logger.debug("set_play")
        self._is_playing = True
        self.setIcon(self.pause_icon)

    def set_pause(self):
        logger.debug("set_pause")
        self._is_playing = False
        self.setIcon(self.play_icon)
