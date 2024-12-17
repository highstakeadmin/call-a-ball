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

import json
import logging

import h5py

logger = logging.getLogger(__name__)


def read_camera_config(config_path: str, height: int, width: int):
    logger.info("read_config")

    if is_json(config_path):
        logger.info("read JSON config")
        with open(config_path, "r") as f:
            try:
                camera = json.load(f)
            except Exception:
                raise Exception("Error reading JSON config file.")
    elif is_hdf5(config_path):
        logger.info("read HDF5 config")
        with h5py.File(config_path, "r") as f:
            try:
                camera = hdf5_conf_to_dict(f, [height, width])
            except Exception:
                raise Exception("Error reading HDF5 config file.")
    else:
        raise Exception("Error reading config file. Unknown format")
    return camera


def hdf5_conf_to_dict(conf, frame_resolution: [int, int]):
    param = conf["/camera/param"][0, 0, 0, :]
    (fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, k5, k6, s1, s2, s3, s4, tx, ty) = param
    (height, width) = frame_resolution
    fx *= width
    fy *= height
    cx = (cx + 0.5) * width
    cy = (cy + 0.5) * height

    return {
        "intrinsics": {
            "camera_matrix": [[fx, 0.0, cx], [0.0, fy, cy], [0.0, 0.0, 1.0]],
            "distortion_coefficients": [
                k1,
                k2,
                p1,
                p2,
                k3,
                k4,
                k5,
                k6,
                s1,
                s2,
                s3,
                s4,
                tx,
                ty,
            ],
        }
    }


def is_json(file_path):
    try:
        with open(file_path, "r") as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return False


def is_hdf5(file_path):
    try:
        with h5py.File(file_path, "r"):
            return True
    except (OSError, IOError):
        return False
