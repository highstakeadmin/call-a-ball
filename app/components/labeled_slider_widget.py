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

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QSlider, QSpinBox

logger = logging.getLogger(__name__)


class LabeledSliderWidget(QWidget):
    on_change = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slider = None
        self.input = None
        QTimer.singleShot(0, self.init_ui)

    def init_ui(self):
        logger.info("init_ui")
        self.input = self.findChild(QSpinBox)
        self.slider = self.findChild(QSlider)

        self.slider.valueChanged.connect(self.set_value)
        self.input.valueChanged.connect(self.set_value)

    def _prepare_value(self, raw_value):
        logger.debug(f"_prepare_value: {raw_value}")
        if self.property("valueParity") == "odd":
            value = raw_value - 1 if raw_value % 2 == 0 else raw_value
        else:
            value = raw_value
        return value

    def set_max(self, value: int):
        logger.debug(f"set_max: {value}")
        self.slider.setMaximum(value)
        self.input.setMaximum(value)

    def set_min(self, value: int):
        logger.debug(f"set_min: {value}")
        self.slider.setMinimum(value)
        self.input.setMinimum(value)

    def set_value(self, raw_value: int):
        value = self._prepare_value(raw_value)
        logger.debug(f"set_value: {value}")
        self.slider.setValue(value)
        self.input.setValue(value)
        self.on_change.emit(value)

    def get_value(self):
        logger.debug(f"get_value")
        return self.slider.value()
