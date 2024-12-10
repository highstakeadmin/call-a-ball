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

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel


def elide_text(label: QLabel, text: str):
    font_metrics = label.fontMetrics()
    elided_text = font_metrics.elidedText(
        text, Qt.TextElideMode.ElideRight, label.width()
    )
    label.setText(elided_text)


def np_to_pixmap(np_img: np.ndarray) -> QPixmap:
    height, width, channel = np_img.shape
    bytes_per_line = 3 * width
    img = QImage(
        np_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
    ).rgbSwapped()
    return QPixmap(img)


def image_to_np(image: QImage) -> np.ndarray or None:
    if image.isNull():
        return None

    incoming_image = image.convertToFormat(QImage.Format.Format_RGB888)

    width = incoming_image.width()
    height = incoming_image.height()

    ptr = incoming_image.bits()
    ptr.setsize(incoming_image.sizeInBytes())
    np_img = np.array(ptr).reshape(height, width, 3)
    return cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
