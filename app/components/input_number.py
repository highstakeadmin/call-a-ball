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

from PyQt6.QtWidgets import QSpinBox
from PyQt6.QtCore import pyqtSignal


class InputNumber(QSpinBox):
    valueSubmitted = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editingFinished.connect(self.handle_editing_finished)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

    def handle_editing_finished(self):
        current_value = self.value()
        self.valueSubmitted.emit(current_value)
