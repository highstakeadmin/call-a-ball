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

from PyQt6 import QtMultimedia
from PyQt6.QtWidgets import QDialog, QListWidget
from PyQt6.uic import loadUi


class CameraSelector(QDialog):
    def __init__(self):
        super(CameraSelector, self).__init__()
        loadUi("ui/select_camera_dialog.ui", self)

        self.list_cameras = self.findChild(QListWidget, "list_cameras")

        available_cameras = QtMultimedia.QMediaDevices.videoInputs()
        for camera_info in available_cameras:
            self.list_cameras.addItem(camera_info.description())
        self.list_cameras.itemSelectionChanged.connect(self.select_camera)

        self.selected_camera = None
        self.camera_index = None

    def select_camera(self):
        selected_items = self.list_cameras.selectedItems()
        if len(selected_items) > 0:
            camera_index = self.list_cameras.row(selected_items[0])
            self.camera_index = camera_index
            self.selected_camera = QtMultimedia.QMediaDevices.videoInputs()[
                camera_index
            ]
        else:
            self.camera_index = None
            self.selected_camera = None
