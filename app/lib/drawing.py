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
import math

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def get_thickness(image) -> int:
    logger.debug(f"get_thickness")
    height, _, _ = image.shape
    k = 1 / 1500
    thickness = math.ceil(height * k)
    if thickness == 1:
        return 2
    return thickness


def get_font_scale(image) -> int:
    height, _, _ = image.shape
    k = 1 / 2000
    font_scale = height * k
    if font_scale < 1:
        return 1
    return font_scale


def draw_contour(image, detection, selected=None):
    logger.debug(f"draw_contour")
    thickness = get_thickness(image)
    height, width, _ = image.shape
    for data in detection:
        if selected is not None and selected["2d_center"] == data["2d_center"]:
            color = (0, 255, 0)
        else:
            color = (0, 255, 255)
        points = np.array(data["2d_contour"], dtype=np.int64)
        contour = points[
            (points[:, 0] >= 0)
            & (points[:, 0] <= width)
            & (points[:, 1] >= 0)
            & (points[:, 1] <= height)
        ].reshape(-1, 1, 2)
        cv2.drawContours(image, [contour], -1, color, thickness)
    return image


def draw_center(image, detection, color=(0, 255, 255)):
    logger.debug(f"draw_center")
    thickness = get_thickness(image)
    line_length = 5 * thickness
    for data in detection:
        center = data["2d_center"]
        center_x = int(center[0])
        center_y = int(center[1])
        if valid_coordinates(center_x, center_y, image):
            cv2.line(
                image,
                (center_x - line_length, center_y),
                (center_x + line_length, center_y),
                color,
                thickness,
            )
            cv2.line(
                image,
                (center_x, center_y - line_length),
                (center_x, center_y + line_length),
                color,
                thickness,
            )
    return image


def draw_lines(image, start_point, end_points):
    logger.debug(f"draw_line")
    color = (0, 255, 0)
    thickness = get_thickness(image)
    start_x = int(start_point["2d_center"][0])
    start_y = int(start_point["2d_center"][1])
    if valid_coordinates(start_x, start_y, image):
        for end_point in end_points:
            end_x = int(end_point["2d_center"][0])
            end_y = int(end_point["2d_center"][1])
            if valid_coordinates(end_x, end_y, image):
                cv2.line(image, (start_x, start_y), (end_x, end_y), color, thickness)
    return image


def draw_text(image, detection, base_point=None):
    logger.debug(f"draw_text")
    thickness = get_thickness(image)
    font_scale = get_font_scale(image)
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (0, 255, 255)

    for i, data in enumerate(detection):
        logger.debug(f"Draw text {data['target']}")
        contour = np.array(data["2d_contour"], dtype=np.int64)
        x, y, w, h = cv2.boundingRect(contour)
        x_txt = (
            data["target"][0]
            if base_point is None
            else data["target"][0] - base_point["target"][0]
        )
        y_txt = (
            data["target"][1]
            if base_point is None
            else data["target"][1] - base_point["target"][1]
        )
        z_txt = (
            data["target"][2]
            if base_point is None
            else data["target"][2] - base_point["target"][2]
        )
        lines = [
            f"X: {round(x_txt, 2)} mm",
            f"Y: {round(y_txt, 2)} mm",
            f"Z: {round(z_txt, 2)} mm",
        ]
        for j, line in enumerate(lines):
            (text_width, text_height), baseline = cv2.getTextSize(
                line, font, font_scale, thickness
            )
            text_x = x + w + 10
            text_y = y + h // 2 + j * int(text_height * 1.5)

            if valid_coordinates(text_x, text_y, image):
                cv2.putText(
                    image,
                    line,
                    (text_x, text_y),
                    font,
                    font_scale,
                    (0, 0, 0),
                    thickness + 4,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    image,
                    line,
                    (text_x, text_y),
                    font,
                    font_scale,
                    color,
                    thickness,
                    cv2.LINE_AA,
                )
    return image


def valid_coordinates(x: int, y: int, image) -> bool:
    height, width, _ = image.shape
    logger.debug(f"valid_coordinates size: {width}, {height} center: {x}, {y}")
    return 0 <= x <= width and 0 <= y <= height
