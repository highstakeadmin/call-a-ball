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
import os

from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QFileDialog

from app.config.constats import FILE_NOT_SELECTED
from app.lib.formaters import elide_text

logger = logging.getLogger(__name__)


class SelectFile(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.btn = None
        self.label = None
        self.window_title = ""
        self.window_filter = ""
        self.file_not_selected = ""
        self.file_path = None
        QTimer.singleShot(0, self.init_ui)

    def init_ui(self):
        logger.debug("init_ui")
        self.btn = self.findChild(QPushButton)
        self.label = self.findChild(QLabel)
        self.window_title = self.property("window_title")
        self.window_filter = self.property("window_filter")
        self.file_not_selected = self.property("file_not_selected") or FILE_NOT_SELECTED
        self.btn.clicked.connect(self.click_handler)

    def click_handler(self):
        logger.debug(f"select_file")

        file_path, _ = QFileDialog.getOpenFileName(
            self, self.window_title, filter=self.window_filter
        )

        if file_path:
            self.file_path = file_path
            file_name = os.path.basename(file_path)
            elide_text(self.label, file_name)
        else:
            self.file_path = None
            self.label.setText(self.file_not_selected)

        self.file_selected.emit(self.file_path)
