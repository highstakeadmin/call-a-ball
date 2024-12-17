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

from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import QPushButton, QStyle
from PyQt6.uic import loadUi

from app.windows.settings import SettingsWindow
from app.styles.menu_bar_qss import menu_bar_qss

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.windows.main import CallABall


class MenuBarModule:
    def __init__(self, main_window: "CallABall"):
        self.new_window = None
        self._main_window = main_window

        menu_bar = main_window.menuBar()
        menu_bar.setStyleSheet(menu_bar_qss)
        menu_bar.setNativeMenuBar(False)

        link_button = QAction("Get calibration file", self._main_window)
        link_button.triggered.connect(self.open_link)
        menu_bar.addAction(link_button)

        guide_button = QAction("Guide", self._main_window)
        guide_button.triggered.connect(self.open_guide_window)
        menu_bar.addAction(guide_button)

        about_button = QAction("About", self._main_window)
        about_button.triggered.connect(self.open_about_window)
        menu_bar.addAction(about_button)

        settings_button = QAction("Settings", self._main_window)
        settings_button.triggered.connect(self.open_settings_window)
        menu_bar.addAction(settings_button)

    def open_about_window(self):
        logger.info("open_about_window")
        self.new_window = QtWidgets.QDialog()
        loadUi("ui/about_window.ui", self.new_window)
        self.init_close_btn()
        self.new_window.showFullScreen()

    def open_guide_window(self):
        logger.info("open_guide_window")
        self.new_window = QtWidgets.QDialog()
        loadUi("ui/guide_window.ui", self.new_window)
        self.init_close_btn()
        self.new_window.showFullScreen()

    def open_settings_window(self):
        logger.info("open_settings_window")
        self.new_window = SettingsWindow()
        self.new_window.show()

    def open_link(self):
        logger.info("open_link")
        url = QUrl("https://radiant-metrics.com")
        QDesktopServices.openUrl(url)

    def init_close_btn(self):
        btn_close_about = self.new_window.findChild(QPushButton, "btn_close")
        style = self.new_window.style()
        close_icon = style.standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        btn_close_about.setIcon(close_icon)
        btn_close_about.clicked.connect(self.close_window)

    def close_window(self):
        self.new_window.close()
